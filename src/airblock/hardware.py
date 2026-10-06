"""Read-only BLE diagnostics. There is deliberately no GATT write path.

Each one-shot operation owns a complete scan/connection lifecycle on one event
loop. No heartbeat, notification subscription, pairing request, or firmware
initialization is sent. OS-level BLE discovery traffic still occurs.
"""

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

from .errors import AirblockError, BluetoothError, CleanupError, SafetyError
from .models import SERVICE_UUID, Candidate, Characteristic, Inspection, Service, profile_issues
from .validation import device_identifier, timeout_seconds

T = TypeVar("T")
CLEANUP_TIMEOUT = 5.0


def _bleak() -> tuple[Any, Any]:
    # Optional: the simulator and its examples must work without Bleak installed.
    try:
        from bleak import BleakClient, BleakScanner
    except ImportError as error:
        raise BluetoothError(
            'Install Bluetooth support: python -m pip install -e ".[ble]"'
        ) from error
    return BleakScanner, BleakClient


def _sync(operation: Callable[[], Coroutine[Any, Any, T]]) -> T:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(operation())
    raise AirblockError(
        "An event loop is already running. Use the async_scan/async_inspect_device API"
    )


async def async_scan(*, timeout: float = 8, name: str | None = None) -> tuple[Candidate, ...]:
    """Return only Airblock-name/FFE1 candidates, or an explicitly named device.

    A candidate is not verified hardware. Unrelated advertisements are discarded
    from the returned result and are never printed or persistently logged.
    """
    timeout = timeout_seconds(timeout)
    if name is not None and (not isinstance(name, str) or not name.strip()):
        raise ValueError("name must be a nonempty exact advertised name")
    scanner, _ = _bleak()
    try:
        async with asyncio.timeout(timeout + CLEANUP_TIMEOUT):
            found = await scanner.discover(timeout=timeout, return_adv=True)
    except Exception as error:
        raise BluetoothError(
            "Bluetooth scan failed. Check Bluetooth power and the host app's permission; "
            "see docs/macos-setup.md. No automatic retry was attempted."
        ) from error
    candidates = []
    for device, advertisement in found.values():
        local_name = advertisement.local_name or device.name
        services = tuple(sorted(s.lower() for s in advertisement.service_uuids))
        matches = (
            local_name == name
            if name is not None
            else "airblock" in (local_name or "").casefold() or SERVICE_UUID in services
        )
        if matches:
            candidates.append(Candidate(device.address, local_name, services))
    return tuple(sorted(candidates, key=lambda candidate: candidate.device_id))


def scan(*, timeout: float = 8, name: str | None = None) -> tuple[Candidate, ...]:
    """Synchronous, one-shot candidate discovery for ordinary scripts."""
    return _sync(lambda: async_scan(timeout=timeout, name=name))


async def _disconnect(client: Any) -> None:
    try:
        await asyncio.wait_for(client.disconnect(), timeout=CLEANUP_TIMEOUT)
        if client.is_connected:
            raise RuntimeError("Backend still reports connected")
    except Exception as error:
        raise CleanupError(
            "Could not confirm Bluetooth disconnection. Keep propulsion modules detached "
            "and remove the main module's battery. No stop command was sent."
        ) from error


async def async_inspect_device(
    device_id: str, *, confirm_detached: bool = False, timeout: float = 10
) -> Inspection:
    """Connect to one explicit device, snapshot its GATT metadata, then disconnect.

    Caller must have removed every propulsion module. This reports protocol
    mismatch as data, without authorizing commands even on a matching profile.
    Timeout applies separately to target discovery and connection; cleanup is
    bounded to five seconds. No retries or other-device fallbacks occur.
    """
    device_id = device_identifier(device_id)
    timeout = timeout_seconds(timeout)
    if confirm_detached is not True:
        raise SafetyError("Detach every propulsion module, then pass confirm_detached=True")
    scanner, client_type = _bleak()
    client = None
    try:
        async with asyncio.timeout(timeout + CLEANUP_TIMEOUT):
            device = await scanner.find_device_by_address(device_id, timeout=timeout)
        if device is None:
            raise BluetoothError("Selected device was not found. Scan again; no fallback was tried")
        if device.address.casefold() != device_id.casefold():
            raise SafetyError("Scanner returned a different device; connection refused")
        # Use the freshly scanned BLEDevice, not a bare UUID (avoids implicit scans).
        client = client_type(device, timeout=timeout)
        async with asyncio.timeout(timeout):
            await client.connect()
        if not client.is_connected:
            raise BluetoothError("Device did not remain connected; state is unknown")
        services = tuple(
            Service(
                service.uuid.lower(),
                tuple(
                    Characteristic(char.uuid.lower(), tuple(sorted(char.properties)))
                    for char in service.characteristics
                ),
            )
            for service in client.services
        )
        if not client.is_connected:
            raise BluetoothError("Device disconnected during inspection; state is unknown")
        issues = profile_issues(services)
        return Inspection(device_id, services, not issues, issues)
    except AirblockError:
        raise
    except Exception as error:
        raise BluetoothError(
            "Device inspection failed. Keep modules detached; check battery, distance and "
            "Bluetooth permission. No automatic retry was attempted."
        ) from error
    finally:
        # Also attempt cleanup if connect() failed partway through or was cancelled.
        if client is not None:
            await _disconnect(client)


def inspect_device(
    device_id: str, *, confirm_detached: bool = False, timeout: float = 10
) -> Inspection:
    """Synchronous one-shot inspection; BLE resources never escape the event loop."""
    return _sync(
        lambda: async_inspect_device(device_id, confirm_detached=confirm_detached, timeout=timeout)
    )


def set_led(*args: object, **kwargs: object) -> None:
    """Reserved hardware API: fail before importing Bluetooth or connecting."""
    raise SafetyError(
        "Hardware LED writes are disabled: Airblock LED encoding and safe prerequisites "
        "are not independently verified. Use Simulator.set_led() instead."
    )

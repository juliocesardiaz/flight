import asyncio
import builtins
from types import SimpleNamespace

import pytest
from conftest import DEVICE_ID, advertisement, device

from airblock import (
    AirblockError,
    BluetoothError,
    CleanupError,
    SafetyError,
    async_inspect_device,
    async_scan,
    hardware,
    inspect_device,
    scan,
    set_led,
)
from airblock.models import SERVICE_UUID


def test_scan_filters_unrelated_devices_and_never_connects(ble):
    ble.found = {
        "unrelated": (
            device("11111111-2222-3333-4444-555555555555", "Private phone"),
            advertisement("Private phone", ()),
        ),
        "one": (device(), advertisement()),
        "two": (
            device("11111111-2222-3333-4444-666666666666", None),
            advertisement(None, (SERVICE_UUID.upper(),)),
        ),
    }
    result = scan()
    assert len(result) == 2
    assert all(c.name != "Private phone" for c in result)
    assert [call[0] for call in ble.calls] == ["discover"]
    assert ble.calls[0][1] == {"timeout": 8.0, "return_adv": True}


def test_exact_name_filter_is_not_substring_or_automatic_connection(ble):
    ble.found["other"] = (device("11:22:33:44:55:66", "Airblock2"), advertisement("Airblock2"))
    assert len(scan(name="Airblock")) == 1
    assert scan(name="airblock") == ()


def test_scan_falls_back_to_device_name(ble):
    ble.found[DEVICE_ID] = (device(), advertisement(None, ()))
    assert scan()[0].name == "Airblock"


@pytest.mark.parametrize("name", ["", "  ", 123])
def test_invalid_scan_name_precedes_bluetooth(ble, name):
    with pytest.raises(ValueError):
        scan(name=name)
    assert ble.calls == []


def test_scan_error_is_private_and_actionable(ble):
    ble.scan_error = RuntimeError("nearby secret device")
    with pytest.raises(BluetoothError) as error:
        scan()
    assert "permission" in str(error.value)
    assert "secret" not in str(error.value)


def test_inspect_explicit_device_no_commands_and_cleanup(ble):
    report = inspect_device(DEVICE_ID.upper(), confirm_detached=True)
    assert report.device_id == DEVICE_ID
    assert report.profile_matches
    assert not report.hardware_writes_enabled
    assert report.profile_issues == ()
    assert len(report.services[0].characteristics) == 2
    assert [c[0] for c in ble.calls] == ["find", "client", "connect", "disconnect"]
    assert not ble.client.is_connected


def test_unfamiliar_profile_reports_mismatch_and_disconnects(ble):
    ble.services = []
    report = inspect_device(DEVICE_ID, confirm_detached=True)
    assert not report.profile_matches
    assert report.profile_issues
    assert not report.hardware_writes_enabled
    assert ble.calls[-1] == ("disconnect",)


@pytest.mark.parametrize("confirmation", [False, None, 1, "yes"])
def test_requires_literal_detached_confirmation(ble, confirmation):
    with pytest.raises(SafetyError):
        inspect_device(DEVICE_ID, confirm_detached=confirmation)
    assert not ble.calls


@pytest.mark.parametrize(
    "identifier", ["", "Airblock", "FFE1", " aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", None]
)
def test_invalid_identifier_never_scans(ble, identifier):
    with pytest.raises(ValueError):
        inspect_device(identifier, confirm_detached=True)
    assert not ble.calls


@pytest.mark.parametrize("timeout", [0, -1, 61, float("nan"), float("inf"), True, "10"])
def test_invalid_timeout_never_scans(ble, timeout):
    with pytest.raises(ValueError):
        inspect_device(DEVICE_ID, confirm_detached=True, timeout=timeout)
    with pytest.raises(ValueError):
        scan(timeout=timeout)
    assert not ble.calls


def test_target_missing_does_not_fallback(ble):
    ble.target = None
    with pytest.raises(BluetoothError, match="not found"):
        inspect_device(DEVICE_ID, confirm_detached=True)
    assert [c[0] for c in ble.calls] == ["find"]


def test_wrong_target_never_connects(ble):
    ble.target = device("11111111-2222-3333-4444-555555555555")
    with pytest.raises(SafetyError, match="different device"):
        inspect_device(DEVICE_ID, confirm_detached=True)
    assert [c[0] for c in ble.calls] == ["find"]


@pytest.mark.parametrize("fault", [RuntimeError("failed"), TimeoutError()])
def test_failed_partial_connection_disconnects_without_retry(ble, fault):
    ble.connect_error = fault
    with pytest.raises(BluetoothError, match="inspection failed"):
        inspect_device(DEVICE_ID, confirm_detached=True)
    assert [c[0] for c in ble.calls] == ["find", "client", "connect", "disconnect"]
    assert not ble.client.is_connected


def test_real_connect_timeout_cleans_up(ble):
    ble.connect_delay = 5
    with pytest.raises(BluetoothError):
        inspect_device(DEVICE_ID, confirm_detached=True, timeout=1)
    assert ble.calls[-1] == ("disconnect",)
    assert not ble.client.is_connected


def test_find_error_never_constructs_client(ble):
    ble.find_error = TimeoutError()
    with pytest.raises(BluetoothError):
        inspect_device(DEVICE_ID, confirm_detached=True)
    assert [c[0] for c in ble.calls] == ["find"]


def test_disconnect_after_immediate_link_loss(ble):
    ble.connect_stays = True
    with pytest.raises(BluetoothError, match="state is unknown"):
        inspect_device(DEVICE_ID, confirm_detached=True)
    assert ble.calls[-1] == ("disconnect",)


def test_link_loss_during_service_iteration(ble):
    class Services:
        def __iter__(self):
            ble.client.is_connected = False
            return iter([])

    ble.services = Services()
    with pytest.raises(BluetoothError, match="during inspection"):
        inspect_device(DEVICE_ID, confirm_detached=True)
    assert ble.calls[-1] == ("disconnect",)


def test_bad_service_data_also_cleans_up(ble):
    ble.services = [SimpleNamespace(uuid=None)]
    with pytest.raises(BluetoothError):
        inspect_device(DEVICE_ID, confirm_detached=True)
    assert ble.calls[-1] == ("disconnect",)


@pytest.mark.parametrize("failure", ["exception", "still_connected", "timeout"])
def test_cleanup_failure_never_claims_disconnect(ble, monkeypatch, failure):
    if failure == "exception":
        ble.disconnect_error = RuntimeError("transport broke")
    elif failure == "still_connected":
        ble.disconnect_stays = True
    else:
        ble.disconnect_delay = 10
        monkeypatch.setattr(hardware, "CLEANUP_TIMEOUT", 0.01)
    with pytest.raises(CleanupError, match="remove the main module's battery"):
        inspect_device(DEVICE_ID, confirm_detached=True)
    assert ble.calls[-1] == ("disconnect",)


def test_cancellation_cleans_up_and_propagates(ble):
    ble.connect_delay = 10

    async def run():
        task = asyncio.create_task(async_inspect_device(DEVICE_ID, confirm_detached=True))
        await asyncio.sleep(0.01)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert ble.calls[-1] == ("disconnect",)
    assert not ble.client.is_connected


def test_async_api_keeps_lifecycle_on_one_loop(ble):
    async def run():
        candidates = await async_scan()
        return await async_inspect_device(candidates[0].device_id, confirm_detached=True)

    assert asyncio.run(run()).profile_matches


def test_sync_api_rejects_nested_loop_without_leaking_coroutine(ble):
    async def run():
        with pytest.raises(AirblockError, match="event loop"):
            scan()
        with pytest.raises(AirblockError, match="event loop"):
            inspect_device(DEVICE_ID, confirm_detached=True)

    asyncio.run(run())
    assert not ble.calls


def test_hardware_led_is_blocked_before_bluetooth(ble):
    with pytest.raises(SafetyError, match="disabled"):
        set_led(0, 255, 0, device_id=DEVICE_ID, confirm_detached=True)
    assert not ble.calls


def test_missing_optional_bleak_has_install_guidance(monkeypatch):
    original = builtins.__import__

    def no_bleak(name, *args, **kwargs):
        if name == "bleak":
            raise ImportError("missing")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_bleak)
    with pytest.raises(BluetoothError, match="Install Bluetooth support"):
        hardware._bleak()


def test_real_optional_import_does_not_touch_bluetooth():
    scanner, client = hardware._bleak()
    assert scanner.__name__ == "BleakScanner"
    assert client.__name__ == "BleakClient"

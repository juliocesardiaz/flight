import asyncio
from types import SimpleNamespace

import pytest

from airblock import hardware
from airblock.models import NOTIFY_UUID, SERVICE_UUID, WRITE_UUID

DEVICE_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def device(address=DEVICE_ID, name="Airblock"):
    return SimpleNamespace(address=address, name=name)


def advertisement(name="Airblock", services=(SERVICE_UUID,)):
    return SimpleNamespace(local_name=name, service_uuids=list(services))


def service(uuid=SERVICE_UUID, chars=None):
    if chars is None:
        chars = [
            SimpleNamespace(uuid=NOTIFY_UUID, properties=["notify"]),
            SimpleNamespace(uuid=WRITE_UUID, properties=["write-without-response"]),
        ]
    return SimpleNamespace(uuid=uuid, characteristics=chars)


@pytest.fixture
def ble(monkeypatch):
    state = SimpleNamespace(
        found={DEVICE_ID: (device(), advertisement())},
        target=device(),
        services=[service()],
        calls=[],
        connect_error=None,
        disconnect_error=None,
        scan_error=None,
        find_error=None,
        connect_delay=0,
        disconnect_delay=0,
        connect_stays=False,
        disconnect_stays=False,
        client=None,
    )

    class Scanner:
        @staticmethod
        async def discover(**kwargs):
            state.calls.append(("discover", kwargs))
            if state.scan_error:
                raise state.scan_error
            return state.found

        @staticmethod
        async def find_device_by_address(address, **kwargs):
            state.calls.append(("find", address, kwargs))
            if state.find_error:
                raise state.find_error
            return state.target

    class Client:
        def __init__(self, target, **kwargs):
            state.calls.append(("client", target, kwargs))
            assert target is state.target  # A freshly scanned BLEDevice, not a string.
            self.is_connected = False
            self.services = state.services
            state.client = self

        async def connect(self):
            state.calls.append(("connect",))
            self.is_connected = True  # Model a partial connection even on failure.
            if state.connect_delay:
                await asyncio.sleep(state.connect_delay)
            if state.connect_error:
                raise state.connect_error
            if state.connect_stays:
                self.is_connected = False

        async def disconnect(self):
            state.calls.append(("disconnect",))
            if state.disconnect_delay:
                await asyncio.sleep(state.disconnect_delay)
            if state.disconnect_error:
                raise state.disconnect_error
            if not state.disconnect_stays:
                self.is_connected = False

        async def write_gatt_char(self, *args, **kwargs):
            pytest.fail("No hardware command writes are permitted")

        async def read_gatt_char(self, *args, **kwargs):
            pytest.fail("No characteristic reads are part of this milestone")

        async def start_notify(self, *args, **kwargs):
            pytest.fail("No notification subscriptions are part of this milestone")

        async def pair(self, *args, **kwargs):
            pytest.fail("No pairing commands are part of this milestone")

    monkeypatch.setattr(hardware, "_bleak", lambda: (Scanner, Client))
    return state

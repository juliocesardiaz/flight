"""Airblock learning toolkit: simulator first, read-only hardware diagnostics."""

from .errors import AirblockError, BluetoothError, CleanupError, SafetyError
from .hardware import async_inspect_device, async_scan, inspect_device, scan, set_led
from .models import Candidate, Characteristic, Inspection, Service
from .simulator import Simulator

__all__ = [
    "AirblockError",
    "BluetoothError",
    "Candidate",
    "Characteristic",
    "CleanupError",
    "Inspection",
    "SafetyError",
    "Service",
    "Simulator",
    "async_inspect_device",
    "async_scan",
    "inspect_device",
    "scan",
    "set_led",
]

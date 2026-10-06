"""Shared strict validation before any Bluetooth activity."""

import math
import re
from uuid import UUID


def timeout_seconds(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("timeout must be a number from 1 to 60 seconds")
    if not math.isfinite(value) or not 1 <= value <= 60:
        raise ValueError("timeout must be a finite number from 1 to 60 seconds")
    return float(value)


def device_identifier(value: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("Select an exact device UUID from flight scan")
    if re.fullmatch(r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", value):
        return value.upper()
    try:
        normalized = str(UUID(value))
    except (ValueError, AttributeError) as error:
        raise ValueError("Use a device UUID from flight scan, not a Bluetooth name") from error
    if value.lower() != normalized:
        raise ValueError("Use the full hyphenated device UUID from flight scan")
    return normalized


def rgb(red: int, green: int, blue: int) -> tuple[int, int, int]:
    values = (red, green, blue)
    if any(type(value) is not int or not 0 <= value <= 255 for value in values):
        raise ValueError("Each RGB channel must be an integer from 0 to 255")
    return values

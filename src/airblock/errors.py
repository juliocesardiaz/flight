"""Predictable, user-facing failures; hardware state is never inferred from silence."""


class AirblockError(Exception):
    """Base class for expected toolkit errors."""


class SafetyError(AirblockError):
    """An operation is not enabled or its safety preconditions are missing."""


class BluetoothError(AirblockError):
    """Bluetooth discovery or connection failed."""


class CleanupError(BluetoothError):
    """The host could not confirm disconnection; physically remove the battery."""

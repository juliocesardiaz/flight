"""A small, deterministic teaching model. It models no physics or firmware."""

from types import TracebackType

from .errors import AirblockError
from .validation import rgb


class Simulator:
    """Model one RGB indicator entirely in memory, with explicit connection state.

    This is not a BLE mock packet encoder. No Bluetooth dependency is imported.
    """

    def __init__(self) -> None:
        self._connected = False
        self._led = (0, 0, 0)
        self._events: list[tuple[int, int, int]] = []

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def led(self) -> tuple[int, int, int]:
        return self._led

    @property
    def events(self) -> tuple[tuple[int, int, int], ...]:
        return tuple(self._events)

    def connect(self) -> None:
        if self._connected:
            raise AirblockError("Simulator is already connected")
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def set_led(self, red: int, green: int, blue: int) -> None:
        color = rgb(red, green, blue)
        if not self._connected:
            raise AirblockError("Connect the simulator before setting its LED")
        self._led = color
        self._events.append(color)

    def __enter__(self) -> "Simulator":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.disconnect()

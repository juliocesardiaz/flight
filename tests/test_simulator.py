import pytest

from airblock import AirblockError, Simulator


def test_no_implicit_state_change_on_connect_disconnect():
    drone = Simulator()
    assert not drone.connected
    with drone:
        assert drone.connected
        assert drone.led == (0, 0, 0)
        assert drone.events == ()
        drone.set_led(1, 2, 3)
    assert not drone.connected
    assert drone.led == (1, 2, 3)
    assert drone.events == ((1, 2, 3),)
    drone.disconnect()  # Idempotent cleanup, no extra simulated LED command.
    assert drone.events == ((1, 2, 3),)


def test_disconnect_on_program_error():
    drone = Simulator()
    with pytest.raises(RuntimeError), drone:
        raise RuntimeError("student program failed")
    assert not drone.connected


def test_requires_connection_and_rejects_duplicate_connect():
    drone = Simulator()
    with pytest.raises(AirblockError):
        drone.set_led(1, 2, 3)
    with drone, pytest.raises(AirblockError):
        drone.connect()


@pytest.mark.parametrize("value", [-1, 256, 1.5, True, "20", None])
def test_rgb_is_strict_and_state_preserved(value):
    with Simulator() as drone:
        drone.set_led(1, 2, 3)
        with pytest.raises(ValueError):
            drone.set_led(value, 0, 0)
        assert drone.led == (1, 2, 3)
        assert drone.events == ((1, 2, 3),)


def test_rgb_boundaries():
    with Simulator() as drone:
        drone.set_led(0, 255, 0)
        assert drone.led == (0, 255, 0)

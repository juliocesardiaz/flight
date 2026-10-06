"""Variables, conditions and functions; works without Bluetooth or hardware."""

from airblock import Simulator


def show_readiness(drone: Simulator, ready: bool, brightness: int) -> None:
    if ready:
        drone.set_led(0, brightness, 0)
    else:
        drone.set_led(brightness, 0, 0)
    print(f"SIMULATOR LED: {drone.led}")


with Simulator() as drone:
    brightness = 40
    battery_checked = True  # A teaching variable, not an actual battery reading.
    for ready in (False, battery_checked):
        show_readiness(drone, ready, brightness)

print("Finished offline. Change the variables and run again.")

# flight

A small Python learning toolkit for the Makeblock Airblock. Start with variables,
conditions, and functions in a simulator; then inspect a real controller over
Bluetooth from a Mac.

**Alpha, hardware untested. This version does not control flight or real LEDs.**
Live LED encoding is not sufficiently verified, so hardware command writes are
blocked. The real-device milestone is **discovery → explicit device selection →
connection → GATT service inspection → disconnect**, with all propulsion modules
physically detached. No arming, calibration, motor, heartbeat, or firmware
commands are implemented.

## Quick start (no hardware needed)

Python 3.11 or newer; Python 3.12 is the recommended classroom baseline.

```sh
git clone --branch sdk/first-hardware-test https://github.com/juliocesardiaz/flight.git
cd flight
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
flight demo
python examples/first_program.py
```

```python
from airblock import Simulator

brightness = 40
with Simulator() as drone:
    ready = True
    if ready:
        drone.set_led(0, brightness, 0)
    print(drone.led)  # (0, 40, 0), simulated only
```

The simulator models one RGB indicator and connection state. It does not model
firmware, battery measurements, aerodynamics, or flight. It requires no Bluetooth
permissions or BLE package. `events` records exactly the simulated LED changes.

## Student Bluetooth lab

Start with the [student Bluetooth walkthrough](docs/student-bluetooth-test.md):
setup, scan, connection/inspection, expected output, troubleshooting, and a
[results template](docs/student-test-results-template.md). Use Terminal for the
first run; edit in VS Code or Vim. The [M2 Mac setup guide](docs/macos-setup.md)
and [hub-only hardware checklist](docs/hardware-checklist.md) give more detail.

A successful connection does not enable motors. The walkthrough explains what
evidence and safeguards are needed for a later supervised motor bench test.

```sh
python -m pip install -e '.[ble,dev]'
pytest
flight scan --timeout 8
# With all propulsion modules detached, use the selected UUID from this Mac:
flight inspect --device 'UUID_FROM_THIS_MAC' --confirm-detached --timeout 10
```

The placeholder must be replaced with an actual peripheral UUID. `scan` lists
only candidate names/services; it never auto-connects. An alternate, known name
can be selected with `flight scan --name 'EXACT_NAME'`. Names and services are
hints, not authentication. A profile mismatch is reported and cannot unlock
commands. No nearby-device inventory is written to disk.

`inspect` briefly connects and discovers GATT metadata. It sends **zero Airblock
application commands**, makes no characteristic reads, and does not subscribe to
notifications. Normal Bluetooth radio/OS discovery traffic still occurs. The
first connection may require Bluetooth permission for Terminal or VS Code.

`flight led` explains the live-write block and exits with an error; it cannot
send a packet. Do not use this toolkit with attached motor modules.

## Python API

- `Simulator()`: context-managed offline indicator model; `set_led(r, g, b)` accepts
  integers 0–255. Connect explicitly or use `with`.
- `scan(timeout=8, name=None)`: one-shot synchronous candidate discovery.
- `inspect_device(device_id, confirm_detached=True, timeout=10)`: one-shot
  synchronous inspection and disconnect, returning an immutable `Inspection`.
- `async_scan` and `async_inspect_device`: the same operations for an existing
  event loop. See [the async example](examples/inspect_async.py). Keep all Bleak
  operations in one running event loop; do not wrap successive BLE operations
  yourself with separate `asyncio.run` calls.
- `set_led(...)`: reserved hardware entry point; always raises `SafetyError`.

Every real connection uses a freshly scanned BLEDevice for the exact ID, with no
fallback device or retry. Timeouts must be finite and 1–60 seconds; inspection
allows up to the chosen timeout plus 5 seconds for discovery, the chosen timeout
for connection, and 5 seconds for cleanup. Cleanup is attempted after partial
connection failures and cancellation. A cleanup failure reports unknown state:
keep motors detached and remove the hub battery. Disconnect is not a motor stop.

CLI exit codes: 0 success, 2 invalid/blocked/failed operation, 3 no scan candidate,
4 GATT profile mismatch, 130 interrupted. Diagnostics are JSON on stdout and
errors on stderr. Unexpected backend details are not printed by default.

## Development and verification

```sh
python -m pip install -e '.[ble,dev]'
ruff check .
ruff format --check .
mypy
pytest --cov=airblock --cov-branch --cov-report=term-missing --cov-fail-under=90
python -m build
```

CI runs software checks on Linux/Python 3.11 and 3.12 and macOS/Python 3.12.
Mock transports cover selection, profile mismatch, RGB bounds, missing devices,
failed/partial connections, deadlines, cancellation, and cleanup failures. CI
never uses hardware; passing it cannot validate this Airblock or its firmware.

Read [protocol evidence and remaining gates](docs/protocol-status.md) before
considering hardware writes. This implementation is original, not a translation
of the unlicensed community Android project. No upstream source is vendored.
No license grant for this repository is added until its owner chooses one.

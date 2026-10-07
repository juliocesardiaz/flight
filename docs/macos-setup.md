# macOS setup: first Airblock session

Student starting here? Follow the [step-by-step Bluetooth lab](student-bluetooth-test.md)
and use this page for additional detail.

For an Apple Silicon MacBook Air (including M2), using VS Code or Vim.
Prepared for the 7 October 2026 session. This SDK is experimental: no Airblock
was available during development, and no real-device behavior is verified.

**Today's hardware goal is discovery and read-only GATT inspection.** The LED
command protocol is not yet verified; hardware LED control is blocked. The
simulator can be used independently. Follow the [hardware checklist](hardware-checklist.md)
before powering a device.

## 1. Check the tools

Open the Mac's Terminal app. Keep this same app for the first BLE session, even
if you edit in VS Code; that makes Bluetooth permission troubleshooting simpler.
Run:

```sh
python3 --version
python3 -c 'import platform; print(platform.machine())'
git --version
```

This project requires **Python 3.11 or newer**. Prefer an existing,
school-approved native Apple Silicon installation (`arm64`). If Python is
missing or too old, ask school IT for an approved installation. Python.org's
[macOS installers](https://www.python.org/downloads/macos/) include native Apple
Silicon support through universal2 builds. Do not modify Apple's
`/usr/bin/python3`. See [Python's macOS guide](https://docs.python.org/3/using/mac.html).
If Git or developer tools are unavailable, ask IT rather than bypassing a
managed-device restriction.

## 2. Install the project in its own environment

In a directory where you keep your projects:

```sh
git clone --branch sdk/first-hardware-test https://github.com/juliocesardiaz/flight.git
cd flight
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[ble,dev]'
pytest
```

The quotes around `'.[ble,dev]'` matter in the Mac's default zsh shell.
Installation needs network access. Use the project's dependency declarations;
the intended BLE dependency is Bleak 3.0.2. Check what was installed:

```sh
python -c 'import sys; from importlib.metadata import version; print(sys.executable); print(sys.version); print("bleak", version("bleak"))'
flight --help
```

The interpreter path should end in `flight/.venv/bin/python`. If tests fail,
keep the error and stop before hardware testing. Passing tests confirms software
checks only, not compatibility with your Airblock.

If the clone reports that the branch is missing or repository access is denied,
ask the project maintainer for the published branch/access. Do not substitute an
unreviewed fork or an unrelated package named `flight`.

Every new terminal session needs:

```sh
cd /path/to/flight
source .venv/bin/activate
```

Replace `/path/to/flight` with your actual checkout location.

## 3. Run without hardware

Leave the Airblock battery out:

```sh
flight demo
python examples/first_program.py
```

These are simulator exercises. A simulated LED change does not establish that
an LED command is safe or understood by the real device.

### VS Code

Open the `flight` folder, then open `examples/first_program.py`. With the
school-approved Microsoft Python extension, select `.venv/bin/python` using the
Python environment control in the status bar. Run the example from the activated
Terminal above. See [VS Code's environment guide](https://code.visualstudio.com/docs/python/environments).
If an extension install is blocked, use Terminal and Vim; no extension is needed
to run these commands.

### Vim

From the checkout:

```sh
vim examples/first_program.py
```

Press `i` to edit, `Esc` then `:wq` and Enter to save and exit. Run the example
with `python examples/first_program.py` in the activated terminal.

## 4. Bluetooth permission and first connection

After completing the physical setup in the [checklist](hardware-checklist.md),
turn on Bluetooth and run:

```sh
flight scan --timeout 8
```

When macOS asks to allow Bluetooth for the app running Python, approve it only
if school policy permits. If you denied it earlier, use **System Settings →
Privacy & Security → Bluetooth** for that app. Terminal and VS Code can have
separate permissions; using VS Code's integrated terminal may change which app
needs permission. Ask IT if the setting is managed. Bleak cannot re-prompt after
a denial. See [Bleak's macOS permissions](https://bleak.readthedocs.io/en/latest/backends/macos.html#permissions).

The scan shows matching Airblock/service candidates, not an inventory of all
nearby devices. A candidate is not proof of identity. If your own Airblock has a
known different advertised name, use the exact name:

```sh
flight scan --name 'EXACT_NAME' --timeout 8
```

On macOS, copy the **device UUID from this Mac's scan**, not a printed MAC address
or another student's UUID. Device UUIDs identify peripherals locally to the
scanning Mac. They are different from service/characteristic UUIDs.
See [Bleak's macOS device identifiers](https://bleak.readthedocs.io/en/latest/backends/macos.html#specific-features-for-the-macos-backend).

With the correct device identified and every propulsion module detached:

```sh
flight inspect --device 'UUID_FROM_THIS_MAC' --confirm-detached --timeout 10
```

Replace the placeholder. Inspection connects only to that explicit target,
lists service and characteristic UUIDs/properties, then disconnects. It sends
zero application command bytes; Bluetooth connection/service-discovery traffic
still occurs. It does not read characteristic values or subscribe to
notifications. `--confirm-detached` is your physical confirmation, not a sensor
check. **Stop here.** Do not attempt LED writes or motion commands.

## If something goes wrong

- **`flight: command not found` / missing module:** activate `.venv`; rerun the
  editable install using `python -m pip`, not an unrelated `pip`.
- **Install or TLS/certificate error:** keep the exact error and ask IT. Do not
  disable certificate checks or use `sudo pip`.
- **Bluetooth denied/unavailable:** check Bluetooth power and the launching
  app's permission. Do not reset privacy controls or remove management profiles.
- **Permission-related crash:** stop and retain the crash/error text. Bleak
  documents application usage-description issues; do not patch a signed app's
  `Info.plist`. See [Bleak troubleshooting](https://bleak.readthedocs.io/en/latest/troubleshooting.html#macos-bugs).
- **No candidate or timeout:** keep modules detached, verify the hub is powered,
  close any phone app using it, and retry near the hub. Use a known exact name
  when appropriate. Do not broaden the test to unfamiliar devices.
- **Several candidates or unexpected services:** stop and confirm device
  identity with the teacher. Do not guess a writable characteristic.

Record the macOS version (`sw_vers`), Python/Bleak versions, commit
(`git rev-parse HEAD`), command, and error or inspection output. Share only the
selected device's details; omit unrelated nearby-device information. No firmware
updates, pairing workarounds, drivers, or packet-capture profiles are required
for this milestone.

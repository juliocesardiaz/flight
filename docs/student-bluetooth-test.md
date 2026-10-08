# Student lab: test Bluetooth on the Airblock

**Goal:** find your Airblock, connect to it, inspect its Bluetooth services, and
finish disconnected. Record what happened so we can decide the next step.

Use your M2 MacBook Air and Terminal. You can edit Python in VS Code or Vim.
This toolkit is experimental. BLE discovery and service inspection have been
observed on one controller; see the [recorded scope](protocol-status.md).
**The current version cannot run motors or real LEDs, even after it connects.**

## 1. Get ready with your teacher

- Get approval for Bluetooth and software installation on the school Mac. If
  something is blocked, ask your teacher or IT. Do not work around school controls.
- Follow the [hub-only hardware checklist](hardware-checklist.md), including
  battery precautions. With the battery removed, detach **every motor/propeller
  module**. Keep the modules separate throughout this lab. Your teacher checks
  the setup before you insert the battery.
- Only test your own or school-authorized controller. Close any phone/tablet app
  already using it. Keep other Airblocks powered off when possible.
- Keep the battery out until step 3. Use the supplied kit manual for safe handling.

## 2. Set up Python and check the software

Use Python 3.11 or newer (3.12 recommended). If you need Python or Git, follow
[Mac setup](macos-setup.md) with your teacher before continuing.

For a **new checkout**, run one line at a time:

```sh
git clone --branch sdk/first-hardware-test https://github.com/juliocesardiaz/flight.git
cd flight
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[ble,dev]'
pytest
flight demo
```

For an **existing checkout**, first run `git status --short`. If it shows edits,
ask your teacher to help preserve them; do not reset or delete them. Otherwise:

```sh
git fetch origin
git switch sdk/first-hardware-test
git pull --ff-only origin sdk/first-hardware-test
source .venv/bin/activate
python -m pip install -e '.[ble,dev]'
pytest
flight demo
```

If `.venv` does not exist, create it with `python3 -m venv .venv` first. If Git
reports a conflict or divergent history, stop and ask your teacher.

**Expected:** tests pass; the demo prints three `SIMULATOR LED:` lines and
`Simulator disconnected. No Bluetooth was used.` No physical LED should change.
If tests fail, save the error and stop before hardware testing.

## 3. Scan: can the Mac see it?

Have your teacher finish the hub-only setup and insert the battery. Turn on
Bluetooth on the Mac. In the same activated Terminal, run:

```sh
flight scan --timeout 8
echo "Scan exit code: $?"
```

Run the `echo` line immediately after `flight`; another command would replace
its exit code. Allow Terminal's Bluetooth prompt only if school policy permits.
If access was previously denied, check **System Settings → Privacy & Security →
Bluetooth**. Terminal and VS Code may need separate permissions. Managed setting?
Ask IT. [Bleak's permission guide](https://bleak.readthedocs.io/en/latest/backends/macos.html#permissions).

**Expected:** a JSON list of candidates, each with `device_id`, `name`, and
`advertised_services`, followed by exit code `0`. An illustrative candidate:

```json
[
  {
    "device_id": "11111111-2222-3333-4444-555555555555",
    "name": "Airblock",
    "advertised_services": ["0000ffe1-0000-1000-8000-00805f9b34fb"]
  }
]
```

This is sample output, not a tested device or an ID to paste. Names can differ
and the advertised service list can be empty. A real controller was observed
advertising `Makeblock_LE` followed by 12 hexadecimal digits, with no service
UUIDs; `flight scan` now includes that name format as a candidate. Other
Makeblock products can use similar names. Copy your own `device_id` only
after your teacher confirms which candidate is your controller. If several
remain, compare scans with your hub powered off/on under supervision. Do not
choose the first result just because it says Airblock.

On macOS the device ID is a UUID from **this Mac**, not the service UUID, a MAC
address, or an ID copied from another student's computer.
[Bleak's device-ID explanation](https://bleak.readthedocs.io/en/latest/backends/macos.html#specific-features-for-the-macos-backend).

**No result?** `[]` with exit code `3` means no matching candidate. Check power,
proximity, Bluetooth permission, and whether another app is connected. Retry
only after checking these. If you know your controller's exact alternate name:

```sh
flight scan --name 'EXACT_NAME' --timeout 8
```

Replace `EXACT_NAME`; don't guess other devices' names. You do not need to pair
in System Settings or install the blocked official app for this diagnostic.

## 4. Connect, inspect, and disconnect

Check again that every propulsion module is detached. Replace the placeholder
below with your selected `device_id`, keeping the quotes:

```sh
flight inspect --device 'UUID_FROM_THIS_MAC' --confirm-detached --timeout 10
echo "Inspect exit code: $?"
```

`--confirm-detached` records your physical check; software cannot check this for
you. This one command connects, lists GATT service/characteristic metadata, and
disconnects. There is no separate `flight connect` command. Allow about 30 seconds
for discovery, connection, and cleanup with these settings.

**Expected:** a JSON object containing `device_id`, `services`, `profile_matches`,
`profile_issues`, and `hardware_writes_enabled`.

- Exit `0`, `profile_matches: true`, and `profile_issues: []`: inspection and
  cleanup succeeded and the service layout matches the expected family profile.
- `hardware_writes_enabled: false` is expected. It stays false after success.
- Exit `4`, `profile_matches: false`: connection/inspection and cleanup completed,
  but the service layout differs. Keep `profile_issues` for your teacher; stop here.
- Exit `2`: invalid input, a blocked operation, or a Bluetooth/cleanup failure.
  Read the error; do not claim the connection succeeded.
- Exit `130`: interrupted. Record it as incomplete.

The program sends no Airblock application commands, reads no characteristic
values, and subscribes to no notifications. Bluetooth connection/discovery
traffic still occurs. No LED or motor movement is expected. A matching service
layout does not verify firmware or a motor-control protocol.

If disconnection cannot be confirmed, keep modules detached and have the teacher
remove the hub battery. Disconnecting or pressing Ctrl-C is **not a motor stop**.

## 5. Record your result, then power down

After the command finishes, have your teacher remove the battery. Keep the
motor modules detached for any further tests with this version.

Copy [this results template](student-test-results-template.md) into a local note
outside the repository. Record the command, exit code, and selected controller's
inspection output. Record versions with:

```sh
sw_vers
python --version
python -c 'from importlib.metadata import version; print("bleak", version("bleak"))'
git rev-parse HEAD
```

Share the note privately with your teacher. Omit your username/home directory,
other devices' identifiers, passwords, tokens, and unrelated logs. Replace the
selected `device_id` with `[REDACTED]` in a shared copy; your local copy can retain
it for a later scan. Leave service/characteristic UUIDs and properties intact.
Do not commit raw diagnostics or student personal details to GitHub.

## 6. If it connects, can we run the motors?

**Not with this version. Stop after inspection.** It has no motor command and
no verified motor-stop or link-loss behavior. Do not run a launch, initialization,
calibration, or copied raw-byte example to see what happens.

Bring your successful inspection and the kit's exact model/manual to your
teacher. Firmware can stay **unknown** until there is an approved way to identify
it. The maintainer needs verified, model-specific start/speed/stop packets,
acknowledgments, and failure behavior before providing a reviewed motor test.
See the [motor-test readiness gate](protocol-status.md#motor-test-readiness-gate).

A later test would need teacher supervision, a secured bench fixture, a
manufacturer-supported way to remove propellers safely, a conservative speed
and short fixed duration, and independently verified stop and link-loss behavior
with a safe physical power cutoff. If safe propeller removal or these safeguards
cannot be established, do not do the motor test. Free flight is outside this lab.

For now, completing Bluetooth inspection and reporting it accurately is the
finished lab. You can keep programming with `examples/first_program.py` in the
simulator while the hardware protocol is reviewed.

## Quick troubleshooting

- **`flight: command not found`:** activate `.venv` and rerun the editable install.
- **Permission denied:** check the launching app's Bluetooth permission; ask IT
  if managed. Do not reset school privacy controls or edit a signed app.
- **Selected device not found:** scan again on the same Mac and recheck identity.
- **Unexpected services:** report the mismatch; do not choose a writable UUID.
- **Battery heat, swelling, damage, moisture, or odor:** stop, step away, and alert
  the teacher. Do not handle a suspect battery.

More detail: [Mac troubleshooting](macos-setup.md#if-something-goes-wrong).

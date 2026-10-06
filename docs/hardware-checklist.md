# Airblock first-hardware-test checklist

Session: **7 October 2026** · Target: student M2 MacBook Air · Scope: one owned or
school-authorized Airblock main controller, all propulsion modules detached.

**Status at preparation: hardware untested. LED protocol unverified and blocked.**
The permitted endpoint is a successful scan, explicit-device GATT inspection,
and disconnect. It is useful to finish here even if the LED milestone is not
ready. No flight, hovercraft movement, motor, arming, calibration, heartbeat, or
firmware command belongs in this session.

## A. Before the session

- [ ] Complete [macOS setup](macos-setup.md), including `pytest`, `flight demo`,
  and `python examples/first_program.py`.
- [ ] Have a teacher/responsible adult supervise the hardware and battery.
- [ ] Read the supplied Airblock manual. The official
  [Makeblock Airblock manual](https://cdnlab.makeblock.com/Airblock-V1.0_STD_EN_User%20Manual_D1.4.6_7.40.4602_Print.pdf)
  covers battery use (printed page 5) and rotating-part warnings (printed page
  13). The official download returned a server error during preparation; do not
  bypass a browser security warning if the link is unavailable. Use the manual
  supplied with the kit.
- [ ] Obtain school approval for Python installation and Bluetooth use if
  needed. If blocked, use the simulator and ask IT; keep device management intact.

## B. Make a hub-only bench setup

These are conservative precautions for this experimental SDK, not a claim that
the manufacturer has approved this software or this test procedure.

1. **Remove the battery before changing the module arrangement.** Airblock has
   no physical power switch: inserting the battery powers the main controller
   into standby. Do not treat standby as powered off.
2. Detach **all six motor/propeller power modules** from the main controller.
   Move them away so their magnetic connectors cannot accidentally reattach.
   Removing covers or restraining an assembled aircraft does not meet this step.
3. Inspect the controller, connectors, battery, and charger. Do not use damaged,
   swollen, leaking, or unusually hot equipment. Use the specified Airblock
   battery and charger, under adult supervision; keep terminals from shorting.
4. Place only the main controller on a dry, clear, stable surface, away from
   liquids, loose metal, hair, and hands. Keep the detached modules separate.
5. Close any phone/tablet app already connected to this Airblock. Keep other
   students' controllers powered off when possible to avoid identification errors.
6. Have the adult verify that no propulsion module remains attached. Only then
   insert the battery with the correct orientation. Keep it accessible for
   removal when the test finishes.

Makeblock's manual warns that rotating propellers can injure, that moisture and
debris can damage the equipment, and that battery handling needs supervision.
The isolation steps above are our additional test controls.
[Source: Airblock manual, pp. 5 and 13](https://cdnlab.makeblock.com/Airblock-V1.0_STD_EN_User%20Manual_D1.4.6_7.40.4602_Print.pdf).

## C. Identify the device without connecting

In the activated project environment:

```sh
flight scan --timeout 8
```

- [ ] Resolve any allowed macOS Bluetooth prompt; see the setup guide.
- [ ] Confirm a candidate belongs to your Airblock. Matching names/services are
  hints, not authentication.
- [ ] If several candidates remain, stop. With adult supervision and modules
  still detached, compare scans with only your hub powered off/on, or otherwise
  establish identity before proceeding. Never select the first row blindly.
- [ ] For a known alternate name, use `flight scan --name 'EXACT_NAME' --timeout 8`.
  Do not guess unrelated names to inventory the room.
- [ ] Copy the device UUID from this Mac's scan. A UUID from another Mac or a
  service UUID is not the right target. [Bleak macOS reference](https://bleak.readthedocs.io/en/latest/backends/macos.html#specific-features-for-the-macos-backend).

If no device appears, verify power, Bluetooth permission, proximity, and that
another app is disconnected. Do not change firmware, run a pairing script, or
send discovery commands to characteristics as a workaround.

## D. Inspect exactly that controller

Check again that every propulsion module is physically detached. Replace the
placeholder with the device UUID just recorded:

```sh
flight inspect --device 'UUID_FROM_THIS_MAC' --confirm-detached --timeout 10
```

- [ ] The target matches the selected controller.
- [ ] Output lists GATT services and characteristic UUIDs/properties.
- [ ] The command returns after disconnecting; record any failure instead of
  assuming success.
- [ ] Save the output locally for protocol review, with date, macOS/Python/Bleak
  versions and `git rev-parse HEAD`.

This command sends **zero application command bytes**. It only connects,
discovers GATT structure, and disconnects; normal BLE transport traffic still
occurs. A property such as `write` or `write-without-response` says what a
characteristic supports, not what Airblock commands mean. Do not experiment
with writes. Do not add characteristic reads, notification subscriptions, or
an initialization/heartbeat message to “make it work.”

A successful inspection establishes BLE access to that unit on that Mac. It
cannot validate command encoding, LED control, battery telemetry, or motion.

## E. Stop and record the result

- [ ] Remove the battery after the inspection has disconnected. Leave the
  propulsion modules detached for any later SDK tests.
- [ ] Mark each outcome honestly: software tests passed/failed; scan
  passed/failed; inspection passed/failed/not run; hardware LED **blocked**.
- [ ] Record any unfamiliar service layout, permissions issue, or timeout for
  the maintainer. Do not publish identifiers or nearby-device logs unnecessarily.

### LED milestone: blocked pending protocol evidence

The simulator's LED API is not permission to transmit its representation over
BLE. Before anyone adds a real LED test, the maintainer must verify the exact
Airblock model/firmware, service and characteristic, complete packet framing,
LED identifier/color encoding, and write mode against authoritative evidence;
review that the packet cannot invoke motion; add byte-level tests; and issue an
updated, reviewed hardware procedure. Inspection results alone cannot remove
this block. **No guessed bytes and no arm/calibrate/motor/heartbeat step.**

### Stop immediately if

- Any propulsion module is still attached, or someone starts reassembling the
  hub while it is powered.
- You are unsure whose device a UUID identifies.
- A test asks for an unexpected write, firmware update, permission escalation,
  school restriction bypass, or undocumented command.
- The battery or hardware becomes hot, swollen, damaged, wet, or emits an odor.
  Step away and alert the supervising adult; do not handle a suspect battery.

Pressing Ctrl-C is not an emergency motor-stop mechanism. This session prevents
that dependency by keeping every motor physically disconnected throughout.

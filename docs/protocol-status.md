# Protocol evidence and safety boundary

Prepared 6 October 2026. This project has not been tested with an Airblock.
These notes distinguish interoperability facts from unverified device behavior.

## What is implemented

The toolkit discovers candidate advertisements and inspects the connected
controller's GATT service metadata. It does not read characteristic values,
subscribe, issue query messages, encode packets, or write characteristics.
The simulator's RGB tuple is an educational state model, not a wire protocol.

The inspected candidate profile is:

| Role | UUID | Checked properties |
| --- | --- | --- |
| Service | `0000ffe1-0000-1000-8000-00805f9b34fb` | Exactly one instance |
| Notify candidate | `0000ffe2-0000-1000-8000-00805f9b34fb` | Notify or indicate |
| Write candidate | `0000ffe3-0000-1000-8000-00805f9b34fb` | Write or write-without-response |

These are Makeblock-family profile hints. They are not unique Airblock identity,
firmware validation, or permission to write. Duplicated, missing, or differently
capable characteristics produce a mismatch. The toolkit never accesses the
separate Makeblock reset service/characteristic.

## Provenance

- Makeblock's official MIT-licensed iPhone application lists the FFE1/FFE2/FFE3
  dual BLE profile in
  [BLEPeripheral.h at commit 824fbd6](https://github.com/Makeblock-official/Makeblock-App-For-iPhone/blob/824fbd68281f84d760340fdabada6673fe35b8d7/Makeblock_iphone/BLE/BLEPeripheral.h).
  Its [implementation](https://github.com/Makeblock-official/Makeblock-App-For-iPhone/blob/824fbd68281f84d760340fdabada6673fe35b8d7/Makeblock_iphone/BLE/BLEPeripheral.m)
  provides Makeblock-family transport context, not an Airblock command specification.
- The archived [MyoAirblock Android reference](https://github.com/Arcaneless/MyoAirblock-android)
  observes the same GATT family on Airblock. It has no explicit reuse license as
  inspected; no implementation was copied, translated, or vendored here.
- Makeblock's MIT-licensed [neuron-engine](https://github.com/Makeblock-official/neuron-engine/tree/87517ccb79b9dc39d544f6a9b34024418c6d49e0)
  documents through its implementation generic Neuron framing and packed data.
  Relevant files: [framing/checksum](https://github.com/Makeblock-official/neuron-engine/blob/87517ccb79b9dc39d544f6a9b34024418c6d49e0/lib/driver/checksum.js),
  [packed field types](https://github.com/Makeblock-official/neuron-engine/blob/87517ccb79b9dc39d544f6a9b34024418c6d49e0/lib/protocol/data.js),
  and [discovery/number assignment](https://github.com/Makeblock-official/neuron-engine/blob/87517ccb79b9dc39d544f6a9b34024418c6d49e0/lib/engine/logic/system.js).
  Those facts do not independently establish Airblock's LED command, channel
  widths, LED index meanings, state prerequisites, or acknowledgments.
- Bluetooth integration follows current official Bleak documentation:
  [scanner](https://bleak.readthedocs.io/en/latest/api/scanner.html),
  [client](https://bleak.readthedocs.io/en/latest/api/client.html),
  [macOS backend](https://bleak.readthedocs.io/en/latest/backends/macos.html), and
  [event-loop requirements](https://bleak.readthedocs.io/en/latest/troubleshooting.html#calling-asyncio-run-more-than-once).
  The tested dependency version is pinned to Bleak 3.0.2.

This is an original diagnostic implementation based on interoperable UUIDs and
public Bleak APIs. Referenced projects retain their own rights and licenses.

## Why the LED gate is closed

No independently verified, authoritative Airblock LED command specification was
located. The community LED encoder has inconsistent reserved field lengths and
packed output lengths, so its transmitted bytes cannot be treated as a trusted
test vector. Firmware and command-state requirements are also unknown.

A community “heartbeat” label is not evidence of a safety watchdog. The
corresponding generic Neuron payload is used for discovery/number assignment in
the vendor engine. Do not assume transmitting it is inert, or that stopping it
lands the aircraft or stops its motors. Likewise, a battery or LED-count query
can require a command write; it is not part of this read-only milestone.

`airblock.set_led` and `flight led` therefore fail immediately. There is no
`--unsafe` switch, raw-byte command, motor API, automatic startup sequence, or
automatic shutdown command. We do not include a guessed protocol encoder or
parser and cannot claim byte-level Airblock protocol tests. Current tests cover
profile parsing, strict input bounds, lifecycle, and simulator behavior.

## Gate for a later LED-only milestone

Before adding a live write path, obtain authoritative Airblock-specific protocol
evidence or an independently validated capture from an authorized control flow.
Record exact model/firmware, full packet bytes, index/color representation,
checksum position, characteristic and explicit write response mode. Confirm the
LED command requires no turn-on/arming/calibration/motion step. Review evidence
and add independently grounded byte-vector and failure tests. Only then conduct
an adult-supervised hub-only LED experiment with every propulsion module
removed; record expected and observed output separately.

If these prerequisites cannot be established, remain at inspection. A successful
BLE connection does not justify experimenting with unrecognized commands.
Live movement is outside this release and needs a separate safety design,
validated control/failsafe behavior, supervision, and appropriate authorization.

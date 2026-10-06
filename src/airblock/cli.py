"""Small CLI; safe JSON output does not execute advertised device names."""

import argparse
import json
import sys
from dataclasses import asdict
from importlib.metadata import version

from .errors import AirblockError
from .hardware import inspect_device, scan, set_led
from .simulator import Simulator


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Airblock simulator and read-only BLE diagnostics")
    parser.add_argument("--version", action="version", version=version("flight-airblock"))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo", help="Run a simulator-only RGB exercise (no Bluetooth)")
    scan_parser = commands.add_parser("scan", help="List candidate advertisements; never connect")
    scan_parser.add_argument("--timeout", type=float, default=8)
    scan_parser.add_argument("--name", help="Only return this exact advertised name")
    inspect_parser = commands.add_parser(
        "inspect", help="Explicit connection for GATT metadata only"
    )
    inspect_parser.add_argument("--device", required=True, help="Exact UUID from scan on this Mac")
    inspect_parser.add_argument("--confirm-detached", action="store_true")
    inspect_parser.add_argument("--timeout", type=float, default=10)
    commands.add_parser("led", help="Explain why hardware LED writes are currently disabled")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            with Simulator() as drone:
                for brightness in (20, 60, 100):
                    drone.set_led(0, brightness, 0)
                    print(f"SIMULATOR LED: {drone.led}")
            print("Simulator disconnected. No Bluetooth was used.")
        elif args.command == "scan":
            candidates = scan(timeout=args.timeout, name=args.name)
            print(json.dumps([asdict(candidate) for candidate in candidates], indent=2))
            if not candidates:
                print("No matching candidates. See docs/macos-setup.md.", file=sys.stderr)
                return 3
        elif args.command == "inspect":
            report = inspect_device(
                args.device, confirm_detached=args.confirm_detached, timeout=args.timeout
            )
            print(json.dumps(asdict(report), indent=2))
            if not report.profile_matches:
                print("GATT profile mismatch. Hardware writes remain disabled.", file=sys.stderr)
                return 4
        elif args.command == "led":
            set_led()
    except (AirblockError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print(
            "Interrupted. Keep modules detached; remove the battery if uncertain.", file=sys.stderr
        )
        return 130
    return 0

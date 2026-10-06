"""Read-only hardware inspection: python examples/inspect_async.py UUID.

Detach all propulsion modules first. This never sends application commands.
"""

import argparse
import asyncio
import json
from dataclasses import asdict

from airblock import async_inspect_device


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("device_uuid")
    parser.add_argument("--confirm-detached", action="store_true", required=True)
    args = parser.parse_args()
    report = await async_inspect_device(args.device_uuid, confirm_detached=args.confirm_detached)
    print(json.dumps(asdict(report), indent=2))


if __name__ == "__main__":
    asyncio.run(main())

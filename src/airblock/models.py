"""Immutable diagnostics. A profile match is not device or firmware authentication."""

from dataclasses import dataclass

# Makeblock-family discovery hints only. See docs/protocol-status.md.
SERVICE_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "0000ffe3-0000-1000-8000-00805f9b34fb"


@dataclass(frozen=True)
class Candidate:
    device_id: str
    name: str | None
    advertised_services: tuple[str, ...]


@dataclass(frozen=True)
class Characteristic:
    uuid: str
    properties: tuple[str, ...]


@dataclass(frozen=True)
class Service:
    uuid: str
    characteristics: tuple[Characteristic, ...]


@dataclass(frozen=True)
class Inspection:
    device_id: str
    services: tuple[Service, ...]
    profile_matches: bool
    profile_issues: tuple[str, ...]
    hardware_writes_enabled: bool = False


def profile_issues(services: tuple[Service, ...]) -> tuple[str, ...]:
    """Check only the observed GATT shape, never authorize command transmission."""
    matches = [s for s in services if s.uuid.lower() == SERVICE_UUID]
    if len(matches) != 1:
        return ("Expected exactly one candidate FFE1 service.",)
    issues = []
    for uuid, required in (
        (NOTIFY_UUID, {"notify", "indicate"}),
        (WRITE_UUID, {"write", "write-without-response"}),
    ):
        chars = [c for c in matches[0].characteristics if c.uuid.lower() == uuid]
        if len(chars) != 1:
            issues.append(f"Expected exactly one {uuid} characteristic in FFE1.")
        elif not required.intersection(chars[0].properties):
            issues.append(f"Unexpected properties for {uuid}.")
    return tuple(issues)

from dataclasses import FrozenInstanceError

import pytest

from airblock.models import (
    NOTIFY_UUID,
    SERVICE_UUID,
    WRITE_UUID,
    Characteristic,
    Service,
    profile_issues,
)
from airblock.validation import device_identifier


def make_service(notify=("notify",), write=("write-without-response",)):
    return Service(
        SERVICE_UUID, (Characteristic(NOTIFY_UUID, notify), Characteristic(WRITE_UUID, write))
    )


def test_valid_profile_is_only_a_shape_check():
    assert profile_issues((make_service(),)) == ()
    assert profile_issues((make_service(("indicate",), ("write",)),)) == ()


@pytest.mark.parametrize(
    "services", [(), (make_service(), make_service()), (Service(WRITE_UUID, ()),)]
)
def test_missing_or_duplicate_service_fails_closed(services):
    assert profile_issues(services)


@pytest.mark.parametrize(
    "characteristics",
    [
        (),
        (Characteristic(NOTIFY_UUID, ("read",)),),
        (
            Characteristic(NOTIFY_UUID, ("notify",)),
            Characteristic(WRITE_UUID, ("write",)),
            Characteristic(WRITE_UUID, ("write",)),
        ),
    ],
)
def test_wrong_or_duplicate_characteristic_fails_closed(characteristics):
    assert profile_issues((Service(SERVICE_UUID, characteristics),))


def test_wrong_properties_fail_closed():
    assert len(profile_issues((make_service(("read",), ("read",)),))) == 2


def test_data_is_immutable():
    with pytest.raises(FrozenInstanceError):
        make_service().uuid = "other"


def test_cross_platform_mac_identifier_is_explicit():
    assert device_identifier("aa:bb:cc:dd:ee:ff") == "AA:BB:CC:DD:EE:FF"


def test_unhyphenated_uuid_rejected():
    with pytest.raises(ValueError):
        device_identifier("a" * 32)

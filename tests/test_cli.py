import json
import runpy

import pytest
from conftest import DEVICE_ID

from airblock import cli
from airblock.cli import main


def test_demo_offline(capsys):
    assert main(["demo"]) == 0
    output = capsys.readouterr().out
    assert "SIMULATOR LED" in output
    assert "No Bluetooth" in output


def test_scan_json_no_private_name_leak(ble, capsys):
    assert main(["scan"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output[0]["device_id"] == DEVICE_ID


def test_empty_scan_exit_code(ble, capsys):
    ble.found = {}
    assert main(["scan"]) == 3
    assert "No matching" in capsys.readouterr().err


def test_inspect_json_and_mismatch_code(ble, capsys):
    assert main(["inspect", "--device", DEVICE_ID, "--confirm-detached"]) == 0
    assert json.loads(capsys.readouterr().out)["hardware_writes_enabled"] is False
    ble.services = []
    assert main(["inspect", "--device", DEVICE_ID, "--confirm-detached"]) == 4
    assert "mismatch" in capsys.readouterr().err


def test_no_unsafe_default(ble, capsys):
    assert main(["inspect", "--device", DEVICE_ID]) == 2
    assert not ble.calls
    assert "Detach" in capsys.readouterr().err
    assert main(["led"]) == 2
    assert not ble.calls
    assert "disabled" in capsys.readouterr().err


def test_invalid_argument_and_version(capsys):
    with pytest.raises(SystemExit) as error:
        main([])
    assert error.value.code == 2
    with pytest.raises(SystemExit) as error:
        main(["--version"])
    assert error.value.code == 0
    assert "0.1.0a1" in capsys.readouterr().out


def test_bad_timeout(ble, capsys):
    assert main(["scan", "--timeout", "nan"]) == 2
    assert not ble.calls


def test_ctrl_c_message(monkeypatch, capsys):
    def interrupt(**kwargs):
        raise KeyboardInterrupt()

    monkeypatch.setattr(cli, "scan", interrupt)
    assert main(["scan"]) == 130
    assert "remove the battery" in capsys.readouterr().err


def test_module_entrypoint(monkeypatch):
    monkeypatch.setattr("sys.argv", ["flight", "demo"])
    with pytest.raises(SystemExit) as error:
        runpy.run_module("airblock", run_name="__main__")
    assert error.value.code == 0

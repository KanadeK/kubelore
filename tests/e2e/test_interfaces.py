import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from kubelore.api import app
from kubelore.cli import main


def test_cli_text_writes_actual_fault_chain(capsys: pytest.CaptureFixture[str]) -> None:
    status = main(["analyze", "examples/bundles/image-not-found.json"])
    rendered = capsys.readouterr().out
    assert status == 0
    assert "ImagePullFailure (94%)" in rendered
    assert "registry.example.invalid/acme/web:3.4.1" in rendered


def test_cli_json_export_is_machine_readable(tmp_path: Path) -> None:
    target = tmp_path / "report.json"
    assert main(["analyze", "examples/bundles/oom.json", "--format", "json", "--output", str(target)]) == 0
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["primary_chain"]["category"] == "OutOfMemory"
    assert payload["primary_chain"]["evidence"][1]["detail"] == "container/worker terminated: OOMKilled"


def test_cli_invalid_input_fails_without_writing_success(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit, match="Expected KubeLore"):
        main(["analyze", str(broken)])
    assert not capsys.readouterr().out


def test_web_index_and_report_are_connected_to_real_bundles() -> None:
    client = TestClient(app)
    index = client.get("/")
    report = client.get("/report/scheduling-failure.json")
    assert index.status_code == 200
    assert "image-not-found" in index.text
    assert report.status_code == 200
    assert "SchedulingFailure" in report.text
    assert "0/2 nodes available" in report.text


def test_web_rejects_unknown_bundle() -> None:
    assert TestClient(app).get("/report/does-not-exist.json").status_code == 404


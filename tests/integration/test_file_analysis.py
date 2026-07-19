from pathlib import Path

import pytest

from kubelore.adapters.files import BundleFormatError, load_bundle
from kubelore.services.analyze import analyze_file

BUNDLES = Path("examples/bundles")


@pytest.mark.parametrize(
    ("filename", "category"),
    [
        ("image-not-found.json", "ImagePullFailure"),
        ("probe-failure.json", "ProbeFailure"),
        ("oom.json", "OutOfMemory"),
        ("config-missing.json", "ConfigurationMissing"),
        ("scheduling-failure.json", "SchedulingFailure"),
    ],
)
def test_each_offline_bundle_has_a_distinct_primary_chain(filename: str, category: str) -> None:
    report = analyze_file(BUNDLES / filename)
    assert report.primary_chain.category == category
    assert report.primary_chain.evidence
    assert report.primary_chain.resource_path[0].startswith("deployment/")


def test_loads_kubernetes_items_style_dump(tmp_path: Path) -> None:
    dump = tmp_path / "dump.json"
    dump.write_text('{"items":[{"kind":"Pod","metadata":{"name":"p"}},{"kind":"Event","lastTimestamp":"2026-01-01T00:00:00Z","reason":"FailedScheduling","message":"no nodes","involvedObject":{"kind":"Pod","name":"p"}}]}', encoding="utf-8")
    bundle = load_bundle(dump)
    assert bundle.name == "dump"
    assert len(bundle.resources) == 1
    assert bundle.events[0].reason == "FailedScheduling"


@pytest.mark.parametrize("content, expected", [("[]", "root"), ("{bad", "valid JSON"), ("{}", "Expected")])
def test_rejects_invalid_input(tmp_path: Path, content: str, expected: str) -> None:
    path = tmp_path / "broken.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(BundleFormatError, match=expected):
        load_bundle(path)


def test_missing_file_is_not_silenced(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_bundle(tmp_path / "missing.json")


"""Build release artifacts, add offline data, checksum them, and smoke-test the wheel."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from kubelore.services.analyze import analyze_file
from kubelore.services.render import render_html

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RELEASE = ROOT / "dist-release"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    subprocess.run([sys.executable, "-m", "build"], cwd=ROOT, check=True)
    RELEASE.mkdir(exist_ok=True)
    artifacts = sorted(DIST.glob("kubelore-0.1.0*"))
    if len(artifacts) < 2:
        raise RuntimeError("Expected a wheel and source distribution in dist/.")
    copied: list[Path] = []
    for artifact in artifacts:
        target = RELEASE / artifact.name
        shutil.copy2(artifact, target)
        copied.append(target)
    bundle_target = RELEASE / "kubelore-0.1.0-offline-bundles"
    bundle_archive = RELEASE / "kubelore-0.1.0-offline-bundles.zip"
    if bundle_target.exists():
        shutil.rmtree(bundle_target)
    shutil.make_archive(
        str(bundle_target),
        "zip",
        root_dir=ROOT / "examples" / "bundles",
    )
    report = RELEASE / "kubelore-0.1.0-image-not-found-report.html"
    report.write_text(render_html(analyze_file(ROOT / "examples" / "bundles" / "image-not-found.json")), encoding="utf-8")
    copied.extend([report, bundle_archive])
    with tempfile.TemporaryDirectory(prefix="kubelore-release-") as temporary:
        venv = Path(temporary) / "venv"
        subprocess.run([sys.executable, "-m", "venv", "--system-site-packages", str(venv)], check=True)
        python = venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        wheel = next(path for path in copied if path.suffix == ".whl")
        subprocess.run([str(python), "-m", "pip", "install", "--no-deps", str(wheel)], check=True)
        subprocess.run([str(python), "-c", "from kubelore.services.analyze import analyze_file; from pathlib import Path; assert analyze_file(Path(r'" + str(ROOT / "examples" / "bundles" / "oom.json") + "')).primary_chain.category == 'OutOfMemory'"], check=True)
    checksum_paths = [path for path in copied if path.is_file()]
    lines = [f"{_sha256(path)}  {path.name}" for path in sorted(checksum_paths)]
    (RELEASE / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

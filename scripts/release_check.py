"""Fail closed when a release prerequisite is absent."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(r"TODO|FIXME|NotImplemented|placeholder|coming soon|lorem ipsum", re.IGNORECASE)
SECRET = re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def main() -> int:
    failures: list[str] = []
    if git("status", "--porcelain"):
        failures.append("working tree is not clean")
    if 'version = "0.1.0"' not in (ROOT / "pyproject.toml").read_text(encoding="utf-8"):
        failures.append("pyproject version is not v0.1.0")
    if "## v0.1.0" not in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"):
        failures.append("CHANGELOG lacks v0.1.0")
    if not (ROOT / "dist-release" / "SHA256SUMS.txt").is_file():
        failures.append("release artifacts or checksums are missing")
    tracked = set(git("ls-files").splitlines())
    for relative in tracked:
        path = ROOT / relative
        if path.name == "release_check.py":
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if FORBIDDEN.search(content):
            failures.append(f"forbidden unfinished marker in {path.relative_to(ROOT)}")
        if SECRET.search(content):
            failures.append(f"possible secret in {path.relative_to(ROOT)}")
    author = git("log", "-1", "--format=%an <%ae> | %cn <%ce>")
    login = subprocess.check_output(["gh", "api", "user", "--jq", ".login"], text=True, encoding="utf-8").strip()
    if not author.startswith(f"{login} <") or f"| {login} <" not in author:
        failures.append("latest author or committer does not match GitHub login")
    result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, check=False)
    if result.returncode:
        failures.append("test suite failed")
    if failures:
        raise SystemExit("release-check failed:\n- " + "\n- ".join(failures))
    print("release-check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

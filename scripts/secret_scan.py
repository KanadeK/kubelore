"""Minimal deterministic secret scan for CI and release checks."""

from __future__ import annotations

from pathlib import Path

from scripts.release_check import SECRET

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    matches = []
    for path in ROOT.rglob("*"):
        if path.is_file() and ".git" not in path.parts and SECRET.search(path.read_text(encoding="utf-8", errors="ignore")):
            matches.append(str(path.relative_to(ROOT)))
    if matches:
        raise SystemExit("possible secrets: " + ", ".join(matches))
    print("secret scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


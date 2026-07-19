"""Cross-platform verification entry point."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    commands = [
        [sys.executable, "-m", "ruff", "check", "."],
        [sys.executable, "-m", "mypy", "src"],
        [sys.executable, "-m", "pytest", "-q", "--cov=src", "--cov-fail-under=80"],
        [sys.executable, "-m", "build"],
    ]
    for command in commands:
        if subprocess.run(command, check=False).returncode:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


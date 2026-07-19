"""Small, conservative redaction helpers for rendered evidence."""

from __future__ import annotations

import re

_KEY_VALUE = re.compile(r"(?i)\b(token|password|secret|authorization)\s*[:=]\s*([^\s,;]+)")
_BEARER = re.compile(r"(?i)bearer\s+[a-z0-9._~+/=-]+")


def redact(value: str) -> str:
    """Hide likely secret values while preserving the evidence's meaning."""
    redacted = _KEY_VALUE.sub(lambda match: f"{match.group(1)}=[REDACTED]", value)
    return _BEARER.sub("Bearer [REDACTED]", redacted)


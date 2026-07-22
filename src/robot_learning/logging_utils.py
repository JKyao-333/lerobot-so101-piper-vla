"""Redaction helpers for logs that may be shared publicly."""

from __future__ import annotations

import re

REDACTIONS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"hf_[A-Za-z0-9]{8,}"), "<HF_TOKEN_REDACTED>"),
    (
        re.compile(
            r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----.*?"
            r"-----END (?:RSA |OPENSSH |EC )?PRIVATE KEY-----",
            re.DOTALL,
        ),
        "<PRIVATE_KEY_REDACTED>",
    ),
    (
        re.compile(r"(?<![./])\b(?:root|ubuntu|admin)@[A-Za-z0-9.-]+\b"),
        "<SSH_TARGET_REDACTED>",
    ),
    (re.compile(r"(?i)\b(?:token|password|secret)\s*[:=]\s*\S+"), "<SECRET_REDACTED>"),
    (re.compile(r"/root/autodl-tmp(?:/[^\s'\"]*)?"), "<REMOTE_PATH_REDACTED>"),
    (re.compile(r"/home/[^/\s]+(?:/[^\s'\"]*)?"), "<HOME_PATH_REDACTED>"),
    (re.compile(r"/Users/[^/\s]+(?:/[^\s'\"]*)?"), "<HOME_PATH_REDACTED>"),
    (re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+(?:\\[^\s'\"]*)?"), "<HOME_PATH_REDACTED>"),
)


def sanitize_text(text: str) -> str:
    sanitized = text
    for pattern, replacement in REDACTIONS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def contains_sensitive_text(text: str) -> bool:
    return sanitize_text(text) != text

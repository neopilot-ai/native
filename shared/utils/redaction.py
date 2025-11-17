"""Utilities for redacting sensitive configuration content.

This module focuses on redacting secrets that commonly appear in JavaScript
framework projects (e.g., Next.js, NestJS) so they can be safely surfaced to
LLM-powered workflows without risking credential leakage.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

_SENSITIVE_KEYWORDS = (
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "API_KEY",
    "APIKEY",
    "ACCESS_KEY",
    "CLIENT_SECRET",
    "DATABASE_URL",
    "SUPABASE",
    "NEXTAUTH",
    "AUTH_SECRET",
)

_REDACTED = "***REDACTED***"

_ENV_LINE_RE = re.compile(
    r"^(?P<key>[A-Za-z0-9_\.\-]+)\s*=\s*(?P<value>.*)$", re.MULTILINE
)
_JSON_PAIR_RE = re.compile(
    r"(?P<prefix>\"?(?P<key>[A-Za-z0-9_\.\-]+)\"?\s*[:=]\s*)(?P<value>\"[^\"]*\"|'[^']*'|[^,\n]+)(?P<suffix>\s*,?)"
)
_SENSITIVE_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.staging",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "next.config.cjs",
    "nest-cli.json",
}


def _is_sensitive_key(key: str) -> bool:
    upper_key = key.upper()
    return any(keyword in upper_key for keyword in _SENSITIVE_KEYWORDS)


def redact_content(content: str) -> str:
    """Redact sensitive values from textual configuration content."""

    def env_replacer(match: re.Match[str]) -> str:
        key = match.group("key")
        value = match.group("value")
        if _is_sensitive_key(key):
            return f"{key}={_REDACTED}"
        return f"{key}={value}"

    redacted = _ENV_LINE_RE.sub(env_replacer, content)

    def json_replacer(match: re.Match[str]) -> str:
        key = match.group("key")
        if _is_sensitive_key(key):
            return f"{match.group('prefix')}{_REDACTED}{match.group('suffix')}"
        return match.group(0)

    return _JSON_PAIR_RE.sub(json_replacer, redacted)


def collect_sensitive_configs(project_root: Path, limit: int = 10) -> Dict[str, str]:
    """Collect redacted snapshots of sensitive config files under *project_root*.

    Args:
        project_root: Base directory to search.
        limit: Maximum number of files to capture to keep prompts concise.

    Returns:
        Mapping of relative file path to redacted content.
    """

    snapshots: Dict[str, str] = {}
    root = project_root.resolve()

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name not in _SENSITIVE_FILE_NAMES and not path.name.startswith(".env"):
            continue
        try:
            content = path.read_text()
        except UnicodeDecodeError:
            continue
        snapshots[str(path.relative_to(root))] = redact_content(content)
        if len(snapshots) >= limit:
            break
    return snapshots


__all__ = ["collect_sensitive_configs", "redact_content"]

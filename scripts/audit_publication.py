from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", ".venv", "node_modules", "outputs", "output", "__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".toml", ".yml", ".yaml", ".sh", ".txt", ".csv", ".gitignore"}
MAX_PUBLIC_FILE_BYTES = 5 * 1024 * 1024

PATTERNS = {
    "absolute_user_path": re.compile(r"/Users/[^/\s]+/"),
    "private_key": re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(r"gh[opsu]_[A-Za-z0-9]{30,}"),
    "generic_secret": re.compile(r"(?i)(?:api[_-]?key|password|client[_-]?secret)\s*[=:]\s*['\"][^'\"]+"),
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
}


def candidates():
    for path in ROOT.rglob("*"):
        if any(part in EXCLUDED_PARTS for part in path.parts) or path.is_dir():
            continue
        yield path


def main() -> int:
    findings: list[str] = []
    checked = 0
    for path in candidates():
        if path.resolve() == Path(__file__).resolve():
            continue
        checked += 1
        relative = path.relative_to(ROOT)
        if path.is_symlink():
            findings.append(f"symlink: {relative}")
            continue
        if path.stat().st_size > MAX_PUBLIC_FILE_BYTES:
            findings.append(f"large_file: {relative} ({path.stat().st_size} bytes)")
        if path.suffix.casefold() not in TEXT_SUFFIXES and path.name != ".gitignore":
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            findings.append(f"unexpected_binary_text: {relative}")
            continue
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                value = match.group(0)
                if label == "email" and value.endswith("@example.test"):
                    continue
                findings.append(f"{label}: {relative}:{text.count(chr(10), 0, match.start()) + 1}")

    print(f"Checked {checked} publication candidates")
    if findings:
        print("Publication audit findings:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Publication audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

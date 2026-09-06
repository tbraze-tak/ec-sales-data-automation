from __future__ import annotations

import re
import subprocess


PATTERNS = {
    "absolute_user_path": re.compile(rb"/Users/[^/\s]+/"),
    "private_key": re.compile(rb"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    "aws_access_key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(rb"gh[opsu]_[A-Za-z0-9]{30,}"),
    "generic_secret": re.compile(
        rb"(?:api[_-]?key|password|client[_-]?secret)\s*[=:]\s*['\"][^'\"]+",
        re.IGNORECASE,
    ),
    "email": re.compile(rb"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
}
EXCLUDED_PATHS = {"scripts/audit_publication.py", "scripts/audit_git_history.py"}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def main() -> int:
    findings: list[str] = []
    objects = git("rev-list", "--objects", "--all").decode().splitlines()
    checked = 0
    seen: set[str] = set()
    for entry in objects:
        object_id, _, path = entry.partition(" ")
        if not path or path in EXCLUDED_PATHS or object_id in seen:
            continue
        seen.add(object_id)
        if git("cat-file", "-t", object_id).strip() != b"blob":
            continue
        data = git("cat-file", "blob", object_id)
        if b"\0" in data:
            continue
        checked += 1
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(data):
                if label == "email" and match.group(0).endswith(b"@example.test"):
                    continue
                line = data.count(b"\n", 0, match.start()) + 1
                findings.append(f"{label}: {path}:{line} ({object_id[:12]})")

    print(f"Checked {checked} committed text blobs")
    if findings:
        print("Git history audit findings:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Git history audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

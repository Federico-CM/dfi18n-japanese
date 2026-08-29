#!/usr/bin/env python3
"""
DFI18n Japanese localization validator.

Current scope:
- Validate dfi18n-data-ja/dfi18n-data/simple/ja.csv

This validator deliberately checks structure and project hygiene only.
It does not attempt to judge Japanese translation quality.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EXPECTED_HEADER = ["text", "translation", "tags"]
TAG_RE = re.compile(r"\[([^\[:]+):([^:\]]+)\]")
KNOWN_ALIGNMENTS = {"LEFT", "RIGHT", "CENTER"}


@dataclass
class Finding:
    severity: str
    message: str
    record: int | None = None

    def render(self) -> str:
        location = f"record {self.record}: " if self.record is not None else ""
        return f"{self.severity}: {location}{self.message}"


def validate_utf8(path: Path) -> tuple[str | None, list[Finding]]:
    findings: list[Finding] = []

    try:
        raw = path.read_bytes()
    except OSError as exc:
        return None, [Finding("ERROR", f"cannot read {path}: {exc}")]

    if raw.startswith(b"\xef\xbb\xbf"):
        findings.append(Finding("ERROR", "UTF-8 BOM present; save as UTF-8 without BOM"))

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        findings.append(
            Finding(
                "ERROR",
                f"invalid UTF-8 at byte {exc.start}: {exc.reason}",
            )
        )
        return None, findings

    if "\ufffd" in text:
        findings.append(
            Finding(
                "ERROR",
                "contains Unicode replacement character U+FFFD, suggesting damaged text/mojibake",
            )
        )

    return text, findings


def validate_tags(tags: str, record_num: int) -> list[Finding]:
    findings: list[Finding] = []

    if not tags:
        return findings

    matches = list(TAG_RE.finditer(tags))

    if not matches:
        findings.append(
            Finding(
                "ERROR",
                f"malformed tags field {tags!r}; expected syntax such as [ALIGNMENT:CENTER]",
                record_num,
            )
        )
        return findings

    # DFI18n extracts tags with a regex rather than requiring the whole field
    # to consist exclusively of tags. For this project, flag leftover text.
    consumed = "".join(match.group(0) for match in matches)
    compact = re.sub(r"\s+", "", tags)
    if consumed != compact:
        findings.append(
            Finding(
                "ERROR",
                f"unparsed text in tags field {tags!r}",
                record_num,
            )
        )

    seen_keys: set[str] = set()

    for match in matches:
        key, value = match.group(1), match.group(2)

        if key in seen_keys:
            findings.append(
                Finding(
                    "WARNING",
                    f"duplicate tag key {key!r}",
                    record_num,
                )
            )
        seen_keys.add(key)

        if key == "ALIGNMENT":
            if value not in KNOWN_ALIGNMENTS:
                findings.append(
                    Finding(
                        "ERROR",
                        f"unknown ALIGNMENT value {value!r}; expected LEFT, RIGHT, or CENTER",
                        record_num,
                    )
                )
        else:
            findings.append(
                Finding(
                    "WARNING",
                    f"unknown tag {key!r}; DFI18n simple translation currently only consults ALIGNMENT",
                    record_num,
                )
            )

    return findings


def validate_simple_csv(path: Path) -> list[Finding]:
    findings: list[Finding] = []

    text, utf8_findings = validate_utf8(path)
    findings.extend(utf8_findings)

    if text is None:
        return findings

    try:
        rows = list(csv.reader(text.splitlines(keepends=True)))
    except csv.Error as exc:
        findings.append(Finding("ERROR", f"invalid CSV: {exc}"))
        return findings

    if not rows:
        findings.append(Finding("ERROR", "CSV is empty"))
        return findings

    header = rows[0]
    if header != EXPECTED_HEADER:
        findings.append(
            Finding(
                "ERROR",
                f"header is {header!r}; expected exactly {EXPECTED_HEADER!r}",
            )
        )

    seen: dict[str, tuple[int, str, str]] = {}

    # csv record 1 is the header. Data begins at logical record 2.
    for record_num, row in enumerate(rows[1:], start=2):
        if len(row) != 3:
            findings.append(
                Finding(
                    "ERROR",
                    f"expected exactly 3 fields, found {len(row)}: {row!r}",
                    record_num,
                )
            )
            continue

        source, translation, tags = row

        if source == "":
            findings.append(Finding("ERROR", "source text is empty", record_num))

        if translation == "":
            findings.append(
                Finding(
                    "WARNING",
                    "translation is empty; verify that deleting the source text is intentional",
                    record_num,
                )
            )

        if source != source.strip():
            findings.append(
                Finding(
                    "WARNING",
                    "source has leading/trailing whitespace; DFI18n simple matching is exact, so verify it is intentional",
                    record_num,
                )
            )

        if "\ufffd" in source or "\ufffd" in translation or "\ufffd" in tags:
            findings.append(
                Finding(
                    "ERROR",
                    "record contains Unicode replacement character U+FFFD",
                    record_num,
                )
            )

        findings.extend(validate_tags(tags, record_num))

        previous = seen.get(source)
        if previous is not None:
            old_record, old_translation, old_tags = previous
            if (translation, tags) == (old_translation, old_tags):
                findings.append(
                    Finding(
                        "ERROR",
                        f"duplicate source text {source!r}; first defined at record {old_record}",
                        record_num,
                    )
                )
            else:
                findings.append(
                    Finding(
                        "ERROR",
                        f"conflicting duplicate source text {source!r}; first defined at record {old_record}",
                        record_num,
                    )
                )
        else:
            seen[source] = (record_num, translation, tags)

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the DFI18n Japanese localization data."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: parent of tools/)",
    )
    args = parser.parse_args()

    repo_root = args.root.resolve()
    simple_csv = (
        repo_root
        / "dfi18n-data-ja"
        / "dfi18n-data"
        / "simple"
        / "ja.csv"
    )

    print(f"Validating: {simple_csv}")

    if not simple_csv.is_file():
        print(f"ERROR: file not found: {simple_csv}")
        return 2

    findings = validate_simple_csv(simple_csv)

    errors = [f for f in findings if f.severity == "ERROR"]
    warnings = [f for f in findings if f.severity == "WARNING"]

    for finding in findings:
        print(finding.render())

    print()
    print(f"Errors:   {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if errors:
        print("RESULT: FAILED")
        return 1

    print("RESULT: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

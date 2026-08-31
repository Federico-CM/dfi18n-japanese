#!/usr/bin/env python3
"""
DFI18n Japanese localization validator.

Current scope:
- Validate dfi18n-data-ja/dfi18n-data/simple/ja.csv
- Detect dfi18n-data-ja/dfi18n-data/rulesets/ja/

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

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

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
        findings.append(
            Finding(
                "ERROR",
                "UTF-8 BOM present; save as UTF-8 without BOM",
            )
        )

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
                "contains Unicode replacement character U+FFFD, "
                "suggesting damaged text/mojibake",
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
                f"malformed tags field {tags!r}; "
                "expected syntax such as [ALIGNMENT:CENTER]",
                record_num,
            )
        )
        return findings

    # DFI18n extracts tags with a regex rather than requiring the whole field
    # to consist exclusively of tags.
    #
    # For this project, permit whitespace outside valid tags, but flag any
    # other unparsed content.
    remaining = TAG_RE.sub("", tags)

    if remaining.strip():
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
                        f"unknown ALIGNMENT value {value!r}; "
                        "expected LEFT, RIGHT, or CENTER",
                        record_num,
                    )
                )
        else:
            findings.append(
                Finding(
                    "WARNING",
                    f"unknown tag {key!r}; "
                    "DFI18n simple translation currently only consults ALIGNMENT",
                    record_num,
                )
            )

    return findings


def validate_ruleset_schema(data: object, path: Path) -> list[Finding]:
    findings: list[Finding] = []

    if not isinstance(data, dict):
        return [
            Finding(
                "ERROR",
                f"ruleset TOML root in {path} must be a table",
            )
        ]

    allowed_top_level = {"base", "rulesets"}

    for key in data:
        if key not in allowed_top_level:
            findings.append(
                Finding(
                    "ERROR",
                    f"unknown top-level field {key!r} in {path}",
                )
            )

    if "base" in data and not isinstance(data["base"], str):
        findings.append(
            Finding(
                "ERROR",
                f"field 'base' in {path} must be a string",
            )
        )

    if "rulesets" not in data:
        findings.append(
            Finding(
                "ERROR",
                f"required field 'rulesets' missing in {path}",
            )
        )
        return findings

    rulesets = data["rulesets"]

    if not isinstance(rulesets, list):
        findings.append(
            Finding(
                "ERROR",
                f"field 'rulesets' in {path} must be an array",
            )
        )
        return findings

    allowed_entry_fields = {"name", "optional", "rules"}

    for index, entry in enumerate(rulesets, start=1):
        location = f"rulesets entry {index} in {path}"

        if not isinstance(entry, dict):
            findings.append(
                Finding(
                    "ERROR",
                    f"{location} must be a table",
                )
            )
            continue

        for key in entry:
            if key not in allowed_entry_fields:
                findings.append(
                    Finding(
                        "ERROR",
                        f"unknown field {key!r} in {location}",
                    )
                )

        if "name" in entry and not isinstance(entry["name"], str):
            findings.append(
                Finding(
                    "ERROR",
                    f"field 'name' in {location} must be a string",
                )
            )

        if "optional" in entry and not isinstance(entry["optional"], bool):
            findings.append(
                Finding(
                    "ERROR",
                    f"field 'optional' in {location} must be a boolean",
                )
            )

        if "rules" not in entry:
            findings.append(
                Finding(
                    "ERROR",
                    f"required field 'rules' missing in {location}",
                )
            )
            continue

        rules = entry["rules"]

        if not isinstance(rules, dict):
            findings.append(
                Finding(
                    "ERROR",
                    f"field 'rules' in {location} must be a table",
                )
            )
            continue

        for source, translation in rules.items():
            if not isinstance(source, str) or not isinstance(translation, str):
                findings.append(
                    Finding(
                        "ERROR",
                        f"rules in {location} must map strings to strings",
                    )
                )
                break

    return findings


def validate_toml_file(
    path: Path,
    ruleset_dir: Path,
) -> tuple[list[Finding], bool]:
    findings: list[Finding] = []

    text, utf8_findings = validate_utf8(path)
    findings.extend(utf8_findings)

    if text is None:
        return findings, False

    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        findings.append(
            Finding(
                "ERROR",
                f"invalid TOML in {path}: {exc}",
            )
        )
        return findings, False

    schema_findings = validate_ruleset_schema(data, path)
    findings.extend(schema_findings)

    schema_valid = not any(
        finding.severity == "ERROR"
        for finding in schema_findings
    )
    is_root_base = (
        schema_valid
        and isinstance(data, dict)
        and "base" not in data
    )

    if isinstance(data, dict):
        relative_path = path.relative_to(ruleset_dir)
        parts = list(relative_path.with_suffix("").parts)

        if parts[-1] == "index":
            parts.pop()

        expected_base = "::".join(parts)
        actual_base = data.get("base", "")

        if isinstance(actual_base, str) and actual_base != expected_base:
            findings.append(
                Finding(
                    "ERROR",
                    f"base namespace mismatch in {path}: "
                    f"expected {expected_base!r}, found {actual_base!r}",
                )
            )

    return findings, is_root_base


def validate_simple_csv(path: Path) -> list[Finding]:
    findings: list[Finding] = []

    text, utf8_findings = validate_utf8(path)
    findings.extend(utf8_findings)

    if text is None:
        return findings

    try:
        rows = list(csv.reader(text.splitlines(keepends=True)))
    except csv.Error as exc:
        findings.append(
            Finding(
                "ERROR",
                f"invalid CSV: {exc}",
            )
        )
        return findings

    if not rows:
        findings.append(
            Finding(
                "ERROR",
                "CSV is empty",
            )
        )
        return findings

    header = rows[0]

    if header != EXPECTED_HEADER:
        findings.append(
            Finding(
                "ERROR",
                f"header is {header!r}; "
                f"expected exactly {EXPECTED_HEADER!r}",
            )
        )

    seen: dict[str, tuple[int, str, str]] = {}

    # CSV record 1 is the header.
    # Data begins at logical record 2.
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
            findings.append(
                Finding(
                    "ERROR",
                    "source text is empty",
                    record_num,
                )
            )

        if translation == "":
            findings.append(
                Finding(
                    "WARNING",
                    "translation is empty; verify that deleting the source text "
                    "is intentional",
                    record_num,
                )
            )

        if source != source.strip():
            findings.append(
                Finding(
                    "WARNING",
                    "source has leading/trailing whitespace; "
                    "DFI18n simple matching is exact, so verify it is intentional",
                    record_num,
                )
            )

        if (
            "\ufffd" in source
            or "\ufffd" in translation
            or "\ufffd" in tags
        ):
            findings.append(
                Finding(
                    "ERROR",
                    "record contains Unicode replacement character U+FFFD",
                    record_num,
                )
            )

        findings.extend(
            validate_tags(
                tags,
                record_num,
            )
        )

        previous = seen.get(source)

        if previous is not None:
            old_record, old_translation, old_tags = previous

            if (translation, tags) == (old_translation, old_tags):
                findings.append(
                    Finding(
                        "ERROR",
                        f"duplicate source text {source!r}; "
                        f"first defined at record {old_record}",
                        record_num,
                    )
                )
            else:
                findings.append(
                    Finding(
                        "ERROR",
                        f"conflicting duplicate source text {source!r}; "
                        f"first defined at record {old_record}",
                        record_num,
                    )
                )
        else:
            seen[source] = (
                record_num,
                translation,
                tags,
            )

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
    ruleset_dir = (
        repo_root
        / "dfi18n-data-ja"
        / "dfi18n-data"
        / "rulesets"
        / "ja"
    )

    print(f"Validating: {simple_csv}")

    if not simple_csv.is_file():
        print(f"ERROR: file not found: {simple_csv}")
        return 2

    findings = validate_simple_csv(simple_csv)

    if ruleset_dir.is_dir():
        toml_files = sorted(ruleset_dir.rglob("*.toml"))
        print(f"Validating rulesets: {ruleset_dir}")

        if not toml_files:
            findings.append(
                Finding(
                    "WARNING",
                    f"ruleset directory contains no TOML files: {ruleset_dir}",
                )
            )

        root_base_file: Path | None = None

        for toml_file in toml_files:
            toml_findings, is_root_base = validate_toml_file(
                toml_file,
                ruleset_dir,
            )
            findings.extend(toml_findings)

            if is_root_base:
                if root_base_file is not None:
                    findings.append(
                        Finding(
                            "ERROR",
                            f"multiple root-base files found: "
                            f"{root_base_file} and {toml_file}",
                        )
                    )
                else:
                    root_base_file = toml_file
    else:
        print(f"Ruleset validation skipped: directory not found: {ruleset_dir}")

    errors = [
        finding
        for finding in findings
        if finding.severity == "ERROR"
    ]

    warnings = [
        finding
        for finding in findings
        if finding.severity == "WARNING"
    ]

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


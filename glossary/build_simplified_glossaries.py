#!/usr/bin/env python3
"""Generate compact glossary variants from extended glossary files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "simplified"

SOURCE_FILES = {
    "reference": ROOT / "glossary_reference.json",
    "alice": ROOT / "glossary_alice.json",
    "custom": ROOT / "glossary_custom_terms.json",
}

# Manual terms should override campaign terms, which should override reference.
MERGE_PRIORITY = ("custom", "alice", "reference")
VERIFIED_STATUSES = {"verified", "from_reference"}


def load_entries(path: Path) -> List[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError(f"Invalid entries list in {path}")
    return entries


def normalize(entries: Iterable[dict], source_name: str) -> List[dict]:
    normalized: List[dict] = []
    for item in entries:
        en = str(item.get("en", "")).strip()
        de = str(item.get("de", "")).strip()
        if not en or not de:
            continue
        normalized.append(
            {
                "en": en,
                "de": de,
                "status": str(item.get("status", "")).strip().lower(),
                "source": source_name,
            }
        )
    return normalized


def sort_entries(entries: Iterable[dict]) -> List[dict]:
    return sorted(entries, key=lambda x: (x["en"].lower(), x["de"].lower()))


def to_simple(entries: Iterable[dict]) -> List[dict]:
    return [{"en": e["en"], "de": e["de"]} for e in entries]


def dedupe_by_en(entries: Iterable[dict]) -> List[dict]:
    seen: Dict[str, dict] = {}
    for item in entries:
        key = item["en"]
        if key not in seen:
            seen[key] = item
    return list(seen.values())


def merge_by_priority(source_entries: Dict[str, List[dict]]) -> List[dict]:
    merged: List[dict] = []
    for name in MERGE_PRIORITY:
        merged.extend(source_entries[name])
    return dedupe_by_en(merged)


def filter_verified(entries: Iterable[dict]) -> List[dict]:
    return [e for e in entries if e["status"] in VERIFIED_STATUSES]


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_tsv(path: Path, entries: Iterable[dict]) -> None:
    lines = [f'{e["en"]}\t{e["de"]}' for e in entries]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    source_entries: Dict[str, List[dict]] = {}
    for source_name, source_path in SOURCE_FILES.items():
        raw_entries = load_entries(source_path)
        source_entries[source_name] = sort_entries(normalize(raw_entries, source_name))

    merged_all = sort_entries(merge_by_priority(source_entries))
    merged_verified = sort_entries(filter_verified(merged_all))

    # Per-source compact outputs
    for source_name, entries in source_entries.items():
        write_json(OUT_DIR / f"{source_name}_simple.json", to_simple(entries))
        write_tsv(OUT_DIR / f"{source_name}_simple.tsv", entries)

    # Merged compact outputs
    write_json(OUT_DIR / "merged_simple.json", to_simple(merged_all))
    write_json(OUT_DIR / "merged_verified_simple.json", to_simple(merged_verified))
    write_tsv(OUT_DIR / "merged_simple.tsv", merged_all)
    write_tsv(OUT_DIR / "merged_verified_simple.tsv", merged_verified)

    # Optional debug-friendly output with minimal metadata
    write_json(OUT_DIR / "merged_with_status.json", merged_all)

    print(f"Wrote simplified glossary files to: {OUT_DIR}")


if __name__ == "__main__":
    main()

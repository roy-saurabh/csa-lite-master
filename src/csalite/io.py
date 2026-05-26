"""
I/O utilities for CSA-lite.

All reading and writing goes through this module.
- Read CSV / JSONL case files
- Write CSV / JSONL scored files
- Validate against JSON schemas using jsonschema
- All outputs sorted deterministically by case_id
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

import pandas as pd

from csalite.constants import DEFAULT_ENCODING

# ── JSON Schema validation ─────────────────────────────────────────────────────


def load_json_schema(schema_path: Path) -> dict[str, Any]:
    """Load a JSON schema from disk."""
    with schema_path.open(encoding=DEFAULT_ENCODING) as fh:
        return json.load(fh)


def validate_record_against_schema(
    record: dict[str, Any],
    schema: dict[str, Any],
) -> list[str]:
    """
    Validate a single record dict against a JSON schema.

    Returns a list of error message strings (empty if valid).
    """
    try:
        import jsonschema
    except ImportError:
        raise ImportError("jsonschema is required for schema validation")

    errors = []
    validator = jsonschema.Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(record), key=str):
        errors.append(f"{'.'.join(str(p) for p in error.path) or '<root>'}: {error.message}")
    return errors


def validate_dataframe_against_schema(
    df: pd.DataFrame,
    schema: dict[str, Any],
) -> dict[str, list[str]]:
    """
    Validate all rows of a DataFrame against a JSON schema.

    Returns dict mapping case_id (or row index) -> list of error strings.
    Only rows with errors are included.
    """
    errors: dict[str, list[str]] = {}
    for _, row in df.iterrows():
        record = _row_to_json_record(row)
        row_errors = validate_record_against_schema(record, schema)
        if row_errors:
            key = str(record.get("case_id", _))
            errors[key] = row_errors
    return errors


def _row_to_json_record(row: pd.Series) -> dict[str, Any]:
    """Convert a DataFrame row to a JSON-serialisable dict."""
    record: dict[str, Any] = {}
    for k, v in row.items():
        if pd.isna(v) if not isinstance(v, (str, bool, list, dict)) else False:
            record[k] = None
        elif isinstance(v, float) and v != v:  # NaN check
            record[k] = None
        elif hasattr(v, "item"):  # numpy scalar
            record[k] = v.item()
        else:
            record[k] = v
    return record


# ── CSV reading ────────────────────────────────────────────────────────────────


def read_cases_csv(path: Path) -> pd.DataFrame:
    """
    Read a CSA-lite cases CSV file.

    Preserves all columns. Strips whitespace from string columns.
    Sorts by case_id for determinism.
    """
    df = pd.read_csv(path, encoding=DEFAULT_ENCODING, dtype=str, keep_default_na=False)
    # Convert empty strings to NaN for numeric interpretation
    df = df.replace({"": None, "nan": None, "NA": None, "N/A": None})
    # Sort deterministically
    if "case_id" in df.columns:
        df = df.sort_values("case_id").reset_index(drop=True)
    return df


def read_sources_csv(path: Path) -> pd.DataFrame:
    """Read a sources manifest CSV."""
    df = pd.read_csv(path, encoding=DEFAULT_ENCODING, dtype=str, keep_default_na=False)
    df = df.replace({"": None, "nan": None})
    return df


# ── JSONL reading ──────────────────────────────────────────────────────────────


def read_cases_jsonl(path: Path) -> pd.DataFrame:
    """Read a CSA-lite cases JSONL file."""
    records: list[dict[str, Any]] = []
    with path.open(encoding=DEFAULT_ENCODING) as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    if "case_id" in df.columns:
        df = df.sort_values("case_id").reset_index(drop=True)
    return df


# ── CSV writing ────────────────────────────────────────────────────────────────


def write_cases_csv(df: pd.DataFrame, path: Path) -> None:
    """
    Write a DataFrame to CSV, sorted by case_id.

    Creates parent directories if needed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if "case_id" in df.columns:
        df = df.sort_values("case_id").reset_index(drop=True)
    df.to_csv(path, index=False, encoding=DEFAULT_ENCODING)


def write_table_csv(df: pd.DataFrame, path: Path) -> None:
    """Write an analysis table DataFrame to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding=DEFAULT_ENCODING)


# ── JSONL writing ──────────────────────────────────────────────────────────────


def write_cases_jsonl(df: pd.DataFrame, path: Path) -> None:
    """
    Write a DataFrame to JSONL (one JSON object per line), sorted by case_id.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if "case_id" in df.columns:
        df = df.sort_values("case_id").reset_index(drop=True)

    with path.open("w", encoding=DEFAULT_ENCODING) as fh:
        for _, row in df.iterrows():
            record = _row_to_json_record(row)
            fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


# ── JSONL iteration ────────────────────────────────────────────────────────────


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Lazily iterate over records in a JSONL file."""
    with path.open(encoding=DEFAULT_ENCODING) as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)

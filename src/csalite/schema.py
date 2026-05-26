"""
JSON Schema loading helpers for CSA-lite.

Provides convenient access to the bundled schemas in the schemas/ directory
relative to the project root. For validation logic, see validation.py.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Locate the schemas directory relative to this file's location.
# Installed layout: src/csalite/schema.py -> ../../schemas/
_THIS_DIR = Path(__file__).parent
_SCHEMAS_DIR = _THIS_DIR.parent.parent / "schemas"


def _schema_path(name: str) -> Path:
    """Return the path to a schema file by stem name (without .schema.json)."""
    return _SCHEMAS_DIR / f"{name}.schema.json"


def load_case_schema() -> dict[str, Any]:
    """Load the case.schema.json file."""
    path = _schema_path("case")
    if not path.exists():
        raise FileNotFoundError(f"Case schema not found at: {path}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_sources_schema() -> dict[str, Any]:
    """Load the sources.schema.json file."""
    path = _schema_path("sources")
    if not path.exists():
        raise FileNotFoundError(f"Sources schema not found at: {path}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_scoring_schema() -> dict[str, Any]:
    """Load the scoring.schema.json file."""
    path = _schema_path("scoring")
    if not path.exists():
        raise FileNotFoundError(f"Scoring schema not found at: {path}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def schemas_dir() -> Path:
    """Return the path to the schemas directory."""
    return _SCHEMAS_DIR

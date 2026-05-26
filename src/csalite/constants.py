"""
Global constants for CSA-lite.

All constants are immutable. No network calls. No side effects.
"""

from __future__ import annotations

import datetime
from typing import Final

# ── Project identity ──────────────────────────────────────────────────────────
PROJECT_NAME: Final[str] = "CSA-Lite"
PROJECT_VERSION: Final[str] = "0.1.0"
PAPER_TITLE: Final[str] = (
    "Context-Sliced AI Assurance Lite: A Reproducible Public-Records Framework "
    "for Deployment-Conditioned Risk Analysis of AI Systems"
)

# ── Case ID ───────────────────────────────────────────────────────────────────
CASE_ID_PREFIX: Final[str] = "CSA-LITE-"
CASE_ID_PATTERN: Final[str] = r"^CSA-LITE-\d{4}$"

# ── Temporal bounds ───────────────────────────────────────────────────────────
MIN_YEAR: Final[int] = 1950
CURRENT_YEAR: Final[int] = datetime.date.today().year

# ── Scoring dimensions ────────────────────────────────────────────────────────
SCORE_DIMENSIONS: Final[tuple[str, ...]] = (
    "decision_criticality",
    "autonomy",
    "vulnerability",
    "oversight",
    "recourse",
    "scale",
    "opacity",
    "monitoring",
)

SCORE_MIN: Final[int] = 0
SCORE_MAX: Final[int] = 2
SCORE_VALUES: Final[tuple[int | None, ...]] = (0, 1, 2, None)

# ── Severity bands ────────────────────────────────────────────────────────────
SEVERITY_BAND_LOW_MAX: Final[int] = 3
SEVERITY_BAND_MODERATE_MAX: Final[int] = 7
SEVERITY_BAND_HIGH_MAX: Final[int] = 11
SEVERITY_BAND_SEVERE_MAX: Final[int] = 16

# Thresholds: [0,3] low, [4,7] moderate, [8,11] high, [12,16] severe
SEVERITY_THRESHOLDS: Final[dict[str, tuple[int, int]]] = {
    "low": (0, 3),
    "moderate": (4, 7),
    "high": (8, 11),
    "severe": (12, 16),
}

# Maximum possible score = 8 dimensions * 2 = 16
MAX_TOTAL_SCORE: Final[int] = 16

# ── Evidence completeness ─────────────────────────────────────────────────────
CONFIDENCE_WEIGHTS: Final[dict[str, float]] = {
    "high": 1.0,
    "medium": 0.66,
    "low": 0.33,
    "unknown": 0.0,
}

# ── Review flags ──────────────────────────────────────────────────────────────
HIGH_MISSINGNESS_THRESHOLD: Final[int] = 3
LOW_SOURCE_QUALITY_THRESHOLD: Final[int] = 2
LOW_ECI_THRESHOLD: Final[float] = 0.5

# ── Source quality ────────────────────────────────────────────────────────────
SOURCE_QUALITY_MIN: Final[int] = 0
SOURCE_QUALITY_MAX: Final[int] = 4

# ── Text limits ───────────────────────────────────────────────────────────────
MAX_EXCERPT_WORDS: Final[int] = 500

# ── File / path constants ─────────────────────────────────────────────────────
DEFAULT_ENCODING: Final[str] = "utf-8"
CSV_DATE_FORMAT: Final[str] = "%Y-%m-%d"

# ── Reproducibility ───────────────────────────────────────────────────────────
RANDOM_SEED: Final[int] = 42

# ── Figure output ─────────────────────────────────────────────────────────────
FIGURE_DPI: Final[int] = 300
FIGURE_FORMATS: Final[tuple[str, ...]] = ("png", "svg")

# ── Disclaimer (canonical) ────────────────────────────────────────────────────
DISCLAIMER: Final[str] = (
    "CSA-lite does not produce legal classifications, compliance determinations, "
    "conformity assessments, or validated harm predictions. EU AI Act Annex III "
    "categories are used only as an analytical reference frame for grouping "
    "documented deployments by use area. The Context Severity Index is a "
    "transparent structured-coding output derived from public-record evidence. "
    "It is not a legal risk class. Public records may be incomplete, biased, "
    "contested, or outdated."
)

"""
Pure scoring functions for CSA-lite.

All functions are stateless and deterministic. No side effects, no I/O.

IMPORTANT: The Context Severity Index (CSI) is a structured-coding output
derived from public-record evidence. It is NOT a legal risk class, compliance
determination, or harm prediction.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from csalite.constants import (
    CONFIDENCE_WEIGHTS,
    HIGH_MISSINGNESS_THRESHOLD,
    LOW_ECI_THRESHOLD,
    LOW_SOURCE_QUALITY_THRESHOLD,
    SCORE_DIMENSIONS,
    SEVERITY_THRESHOLDS,
)
from csalite.enums import ConfidenceLevel, SeverityBand


# ── Low-level helpers ─────────────────────────────────────────────────────────


def _is_null(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, float) and math.isnan(val):
        return True
    if isinstance(val, str) and val.strip() in ("", "nan", "NA", "N/A"):
        return True
    return False


def _coerce_score(val: Any) -> int | None:
    if _is_null(val):
        return None
    try:
        iv = int(val)
        if iv in (0, 1, 2):
            return iv
    except (TypeError, ValueError):
        pass
    return None


def _coerce_confidence(val: Any) -> ConfidenceLevel:
    if _is_null(val):
        return ConfidenceLevel.unknown
    if isinstance(val, ConfidenceLevel):
        return val
    s = str(val).strip().lower()
    try:
        return ConfidenceLevel(s)
    except ValueError:
        return ConfidenceLevel.unknown


def score_to_band(score: int | None) -> SeverityBand:
    """Convert a total score integer to its SeverityBand."""
    if score is None:
        return SeverityBand.unknown
    for band_name, (lo, hi) in SEVERITY_THRESHOLDS.items():
        if lo <= score <= hi:
            return SeverityBand(band_name)
    return SeverityBand.unknown


# ── Core scoring ──────────────────────────────────────────────────────────────


def compute_dimension_scores(row: pd.Series | dict[str, Any]) -> dict[str, int | None]:
    """Extract all 8 dimension scores from a row, returning None for missing."""
    if isinstance(row, pd.Series):
        row = row.to_dict()
    return {dim: _coerce_score(row.get(f"{dim}_score")) for dim in SCORE_DIMENSIONS}


def compute_dimension_confidences(
    row: pd.Series | dict[str, Any],
) -> dict[str, ConfidenceLevel]:
    """Extract all 8 dimension confidence levels from a row."""
    if isinstance(row, pd.Series):
        row = row.to_dict()
    return {
        dim: _coerce_confidence(row.get(f"{dim}_confidence")) for dim in SCORE_DIMENSIONS
    }


def compute_known_count(scores: dict[str, int | None]) -> int:
    """Number of dimensions with non-null scores."""
    return sum(1 for v in scores.values() if v is not None)


def compute_missing_count(scores: dict[str, int | None]) -> int:
    """Number of dimensions with null scores."""
    return sum(1 for v in scores.values() if v is None)


def compute_csi_neutral(scores: dict[str, int | None]) -> int | None:
    """
    Context Severity Index: null treated as 1 (neutral assumption).

    Returns None only if all dimensions are null (undefined corpus).
    """
    if all(v is None for v in scores.values()):
        return None
    return sum(v if v is not None else 1 for v in scores.values())


def compute_csi_zero(scores: dict[str, int | None]) -> int:
    """CSI treating null as 0 (optimistic assumption)."""
    return sum(v if v is not None else 0 for v in scores.values())


def compute_csi_conservative(scores: dict[str, int | None]) -> int:
    """CSI treating null as 2 (conservative assumption)."""
    return sum(v if v is not None else 2 for v in scores.values())


def compute_evidence_completeness_index(
    scores: dict[str, int | None],
    confidences: dict[str, ConfidenceLevel],
) -> float:
    """
    Evidence Completeness Index (ECI) in [0, 1].

    For each dimension:
      - If score is null: weight = 0.0
      - Else: weight = CONFIDENCE_WEIGHTS[confidence]
    ECI = mean of all 8 weights.
    """
    n = len(SCORE_DIMENSIONS)
    if n == 0:
        return 0.0
    total = 0.0
    for dim in SCORE_DIMENSIONS:
        if scores.get(dim) is None:
            total += 0.0
        else:
            conf = confidences.get(dim, ConfidenceLevel.unknown)
            total += CONFIDENCE_WEIGHTS.get(conf.value, 0.0)
    return round(total / n, 4)


def compute_review_flags(
    missing_count: int,
    source_quality_score: int | None,
    sensitivity_band_change: bool,
    context_severity_band: SeverityBand,
    eci: float,
) -> dict[str, bool]:
    """
    Compute all four review flags.

    Returns dict with keys:
      high_missingness_flag, low_source_quality_flag,
      sensitivity_band_change (passed through), review_required_flag
    """
    sq = source_quality_score if source_quality_score is not None else (LOW_SOURCE_QUALITY_THRESHOLD + 1)
    high_missingness = missing_count >= HIGH_MISSINGNESS_THRESHOLD
    low_source_quality = sq <= LOW_SOURCE_QUALITY_THRESHOLD
    high_severity_low_eci = (
        context_severity_band in (SeverityBand.high, SeverityBand.severe)
        and eci < LOW_ECI_THRESHOLD
    )
    review_required = (
        high_missingness or low_source_quality or sensitivity_band_change or high_severity_low_eci
    )
    return {
        "high_missingness_flag": high_missingness,
        "low_source_quality_flag": low_source_quality,
        "sensitivity_band_change": sensitivity_band_change,
        "review_required_flag": review_required,
    }


# ── Row-level scoring ─────────────────────────────────────────────────────────


def score_row(row: pd.Series | dict[str, Any]) -> dict[str, Any]:
    """
    Compute all scoring fields for a single case row.

    Returns a flat dict of computed fields to be merged with the original row.
    Pure function — no I/O, no mutation of the input.
    """
    if isinstance(row, pd.Series):
        row = row.to_dict()

    scores = compute_dimension_scores(row)
    confidences = compute_dimension_confidences(row)

    known_count = compute_known_count(scores)
    missing_count = compute_missing_count(scores)

    csi_neutral = compute_csi_neutral(scores)
    csi_zero = compute_csi_zero(scores)
    csi_conservative = compute_csi_conservative(scores)

    band_neutral = score_to_band(csi_neutral)
    band_zero = score_to_band(csi_zero)
    band_conservative = score_to_band(csi_conservative)

    bands = {band_zero, band_neutral, band_conservative}
    # Remove unknown from comparison since it means data is absent
    known_bands = {b for b in bands if b != SeverityBand.unknown}
    sensitivity_band_change = len(known_bands) > 1

    eci = compute_evidence_completeness_index(scores, confidences)

    sq_raw = row.get("source_quality_score")
    try:
        sq = int(sq_raw) if not _is_null(sq_raw) else None
    except (TypeError, ValueError):
        sq = None

    flags = compute_review_flags(
        missing_count=missing_count,
        source_quality_score=sq,
        sensitivity_band_change=sensitivity_band_change,
        context_severity_band=band_neutral,
        eci=eci,
    )

    return {
        "context_severity_index": csi_neutral,
        "context_severity_band": band_neutral.value,
        "known_dimension_count": known_count,
        "missing_dimensions_count": missing_count,
        "evidence_completeness_index": eci,
        "unknown_as_zero_score": csi_zero,
        "unknown_as_neutral_score": csi_neutral,
        "unknown_as_conservative_score": csi_conservative,
        "unknown_as_zero_band": band_zero.value,
        "unknown_as_neutral_band": band_neutral.value,
        "unknown_as_conservative_band": band_conservative.value,
        **flags,
    }


# ── DataFrame-level scoring ────────────────────────────────────────────────────


def score_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute scoring fields for all rows in df.

    Returns a new DataFrame with original columns plus all computed scoring columns.
    Rows are returned in deterministic order (sorted by case_id).
    """
    if df.empty:
        return df.copy()

    df_sorted = df.sort_values("case_id").reset_index(drop=True)
    computed_rows = [score_row(row) for _, row in df_sorted.iterrows()]
    computed_df = pd.DataFrame(computed_rows)
    result = pd.concat([df_sorted.reset_index(drop=True), computed_df], axis=1)

    # Deduplicate columns (in case any computed field names clash with input)
    result = result.loc[:, ~result.columns.duplicated(keep="last")]
    return result

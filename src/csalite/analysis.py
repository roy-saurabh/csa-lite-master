"""
Analysis table generation for CSA-lite manuscript.

Produces the 7 analysis tables described in the manuscript.
All functions return DataFrames sorted deterministically.
No I/O — callers handle reading/writing via io.py.

Table naming follows the manuscript:
  table_1_csalite_dimensions          — framework metadata (no df needed)
  table_2_corpus_composition_by_annex_area
  table_3_within_category_variance
  table_4_dimension_level_patterns
  table_5_evidence_confidence_by_dimension
  table_6_sensitivity_summary
  table_7_matched_case_contrasts
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from csalite.constants import (
    CONFIDENCE_WEIGHTS,
    DATASET_VERSION,
    DIMENSION_DESCRIPTIONS,
    SCORE_DIMENSIONS,
)
from csalite.enums import SeverityBand
from csalite.sensitivity import compute_band_change_summary, compute_sensitivity_dataframe, find_high_variance_pairs


# ── Helpers ────────────────────────────────────────────────────────────────────


def _safe_median(series: pd.Series) -> float:
    s = series.dropna()
    if s.empty:
        return float("nan")
    return float(s.median())


def _safe_mean(series: pd.Series) -> float:
    s = series.dropna()
    if s.empty:
        return float("nan")
    return round(float(s.mean()), 4)


def _safe_std(series: pd.Series) -> float:
    s = series.dropna()
    if len(s) < 2:
        return float("nan")
    return round(float(s.std()), 4)


def _confidence_weight(val: object) -> float:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return 0.0
    s = str(val).strip().lower()
    return CONFIDENCE_WEIGHTS.get(s, 0.0)


# ── Table 1 ────────────────────────────────────────────────────────────────────


def table_1_csalite_dimensions() -> pd.DataFrame:
    """
    Table 1: CSA-lite dimension reference table.

    No DataFrame input — this is a framework-level metadata table.
    One row per dimension (8 total), with scoring anchors and evidence notes.

    Columns:
      dimension, description, score_0, score_1, score_2,
      evidence_required, missingness_note, dataset_version
    """
    rows = []
    for dim in SCORE_DIMENSIONS:
        info = DIMENSION_DESCRIPTIONS.get(dim, {})
        rows.append(
            {
                "dimension": dim,
                "description": info.get("description", ""),
                "score_0": info.get("score_0", ""),
                "score_1": info.get("score_1", ""),
                "score_2": info.get("score_2", ""),
                "evidence_required": info.get("evidence_required", ""),
                "missingness_note": info.get("missingness_note", ""),
                "dataset_version": DATASET_VERSION,
            }
        )
    return pd.DataFrame(rows)


# ── Table 2 ────────────────────────────────────────────────────────────────────


def table_2_corpus_composition_by_annex_area(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 2: Corpus composition by Annex III area.

    Columns:
      annex_iii_area, n_cases, n_direct, n_analogous, n_comparator, n_unclear,
      n_countries, most_common_deployer_type, median_source_quality,
      median_evidence_completeness, dataset_version
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "annex_iii_area", "n_cases", "n_direct", "n_analogous",
                "n_comparator", "n_unclear", "n_countries",
                "most_common_deployer_type", "median_source_quality",
                "median_evidence_completeness", "dataset_version",
            ]
        )

    rows = []
    for area, group in df.groupby("annex_iii_area"):
        mt = group.get("annex_mapping_type", pd.Series(dtype=str))
        n_direct = (mt == "direct").sum()
        n_analogous = (mt == "analogous").sum()
        n_comparator = (mt == "comparator").sum()
        n_unclear = (mt == "unclear").sum()

        countries = (
            group["country"].dropna().nunique() if "country" in group.columns else 0
        )

        deployer_mode = "unknown"
        if "deployer_type" in group.columns:
            mode = group["deployer_type"].dropna().mode()
            deployer_mode = mode.iloc[0] if not mode.empty else "unknown"

        med_sq = _safe_median(pd.to_numeric(group.get("source_quality_score", pd.Series()), errors="coerce"))
        med_eci = _safe_median(pd.to_numeric(group.get("evidence_completeness_index", pd.Series()), errors="coerce"))

        rows.append(
            {
                "annex_iii_area": area,
                "n_cases": len(group),
                "n_direct": int(n_direct),
                "n_analogous": int(n_analogous),
                "n_comparator": int(n_comparator),
                "n_unclear": int(n_unclear),
                "n_countries": int(countries),
                "most_common_deployer_type": deployer_mode,
                "median_source_quality": round(med_sq, 2) if not math.isnan(med_sq) else None,
                "median_evidence_completeness": round(med_eci, 4) if not math.isnan(med_eci) else None,
                "dataset_version": DATASET_VERSION,
            }
        )

    return pd.DataFrame(rows).sort_values("annex_iii_area").reset_index(drop=True)


# ── Table 3 ────────────────────────────────────────────────────────────────────


def table_3_within_category_variance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 3: Within-category CSI variance by Annex III area.

    Columns:
      annex_iii_area, n_cases, min, q1, median, q3, max, iqr, mean, std,
      n_low, n_moderate, n_high, n_severe, n_high_or_severe,
      variance_interpretation, dataset_version
    """
    if df.empty or "context_severity_index" not in df.columns:
        return pd.DataFrame(
            columns=[
                "annex_iii_area", "n_cases", "min", "q1", "median", "q3", "max",
                "iqr", "mean", "std", "n_low", "n_moderate", "n_high", "n_severe",
                "n_high_or_severe", "variance_interpretation", "dataset_version",
            ]
        )

    rows = []
    for area, group in df.groupby("annex_iii_area"):
        csi = pd.to_numeric(group["context_severity_index"], errors="coerce").dropna()
        band_col = group.get("context_severity_band", pd.Series(dtype=str))

        n_low = (band_col == SeverityBand.low.value).sum()
        n_moderate = (band_col == SeverityBand.moderate.value).sum()
        n_high = (band_col == SeverityBand.high.value).sum()
        n_severe = (band_col == SeverityBand.severe.value).sum()

        if csi.empty:
            row: dict = {
                "annex_iii_area": area,
                "n_cases": len(group),
                "min": None, "q1": None, "median": None, "q3": None,
                "max": None, "iqr": None, "mean": None, "std": None,
            }
        else:
            q1 = float(csi.quantile(0.25))
            q3 = float(csi.quantile(0.75))
            row = {
                "annex_iii_area": area,
                "n_cases": len(group),
                "min": int(csi.min()),
                "q1": round(q1, 2),
                "median": round(float(csi.median()), 2),
                "q3": round(q3, 2),
                "max": int(csi.max()),
                "iqr": round(q3 - q1, 2),
                "mean": round(float(csi.mean()), 4),
                "std": round(float(csi.std()), 4) if len(csi) >= 2 else None,
            }

        std_val = row.get("std")
        if std_val is None or (isinstance(std_val, float) and math.isnan(std_val)):
            interpretation = "Insufficient data"
        elif std_val > 3:
            interpretation = "High within-category variance"
        elif std_val > 1.5:
            interpretation = "Moderate within-category variance"
        else:
            interpretation = "Low within-category variance"

        row.update(
            {
                "n_low": int(n_low),
                "n_moderate": int(n_moderate),
                "n_high": int(n_high),
                "n_severe": int(n_severe),
                "n_high_or_severe": int(n_high + n_severe),
                "variance_interpretation": interpretation,
                "dataset_version": DATASET_VERSION,
            }
        )
        rows.append(row)

    return pd.DataFrame(rows).sort_values("annex_iii_area").reset_index(drop=True)


# ── Table 4 ────────────────────────────────────────────────────────────────────


def table_4_dimension_level_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 4: Dimension-level scoring patterns across the corpus.

    Columns:
      dimension, mean_score, median_score, n_score_0, n_score_1, n_score_2,
      n_missing, missingness_rate, high_score_rate, mean_confidence_weight,
      dataset_version
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "dimension", "mean_score", "median_score",
                "n_score_0", "n_score_1", "n_score_2",
                "n_missing", "missingness_rate", "high_score_rate",
                "mean_confidence_weight", "dataset_version",
            ]
        )

    n_total = len(df)
    rows = []
    for dim in SCORE_DIMENSIONS:
        score_col = f"{dim}_score"
        conf_col = f"{dim}_confidence"

        scores = pd.to_numeric(df.get(score_col, pd.Series(dtype=float)), errors="coerce")
        known = scores.dropna()
        n_missing = int(scores.isna().sum())

        conf_weights = df.get(conf_col, pd.Series(dtype=str)).apply(_confidence_weight)

        rows.append(
            {
                "dimension": dim,
                "mean_score": round(float(known.mean()), 4) if not known.empty else None,
                "median_score": round(float(known.median()), 4) if not known.empty else None,
                "n_score_0": int((known == 0).sum()),
                "n_score_1": int((known == 1).sum()),
                "n_score_2": int((known == 2).sum()),
                "n_missing": n_missing,
                "missingness_rate": round(n_missing / n_total, 4) if n_total > 0 else None,
                "high_score_rate": round(float((known == 2).sum() / n_total), 4) if n_total > 0 else None,
                "mean_confidence_weight": round(float(conf_weights.mean()), 4) if not conf_weights.empty else None,
                "dataset_version": DATASET_VERSION,
            }
        )

    return pd.DataFrame(rows)


# ── Table 5 ────────────────────────────────────────────────────────────────────


def table_5_evidence_confidence_by_dimension(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 5: Evidence confidence distribution by dimension.

    For each dimension, reports the count and proportion of cases at each
    confidence level (high / medium / low / unknown) and the mean confidence
    weight (high=1.0, medium=0.66, low=0.33, unknown=0.0).

    Columns:
      dimension, n_high, n_medium, n_low, n_unknown,
      pct_high, pct_medium, pct_low, pct_unknown,
      mean_confidence_weight, dataset_version
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "dimension", "n_high", "n_medium", "n_low", "n_unknown",
                "pct_high", "pct_medium", "pct_low", "pct_unknown",
                "mean_confidence_weight", "dataset_version",
            ]
        )

    n_total = len(df)
    rows = []
    for dim in SCORE_DIMENSIONS:
        conf_col = f"{dim}_confidence"
        confs = df.get(conf_col, pd.Series(dtype=str)).fillna("unknown")
        confs = confs.apply(lambda v: str(v).strip().lower() if v else "unknown")

        n_high = int((confs == "high").sum())
        n_medium = int((confs == "medium").sum())
        n_low = int((confs == "low").sum())
        n_unknown = int((confs == "unknown").sum() + confs.isin(["", "nan", "n/a"]).sum())

        weights = confs.map(lambda v: CONFIDENCE_WEIGHTS.get(v, 0.0))
        mean_w = round(float(weights.mean()), 4) if n_total > 0 else None

        rows.append(
            {
                "dimension": dim,
                "n_high": n_high,
                "n_medium": n_medium,
                "n_low": n_low,
                "n_unknown": n_unknown,
                "pct_high": round(100 * n_high / n_total, 1) if n_total > 0 else None,
                "pct_medium": round(100 * n_medium / n_total, 1) if n_total > 0 else None,
                "pct_low": round(100 * n_low / n_total, 1) if n_total > 0 else None,
                "pct_unknown": round(100 * n_unknown / n_total, 1) if n_total > 0 else None,
                "mean_confidence_weight": mean_w,
                "dataset_version": DATASET_VERSION,
            }
        )

    return pd.DataFrame(rows)


# ── Table 6 ────────────────────────────────────────────────────────────────────


def table_6_sensitivity_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 6: Sensitivity analysis summary by Annex III area.

    Wraps sensitivity.compute_sensitivity_dataframe + compute_band_change_summary.

    Columns:
      annex_iii_area, n_cases, n_band_changes, pct_band_changes,
      dataset_version
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "annex_iii_area", "n_cases", "n_band_changes",
                "pct_band_changes", "dataset_version",
            ]
        )

    sens_df = compute_sensitivity_dataframe(df)
    summary = compute_band_change_summary(sens_df)
    summary["dataset_version"] = DATASET_VERSION
    return summary


# ── Table 7 ────────────────────────────────────────────────────────────────────


def table_7_matched_case_contrasts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 7: Matched case contrasts within Annex III areas.

    For each area, identifies the lowest- and highest-CSI case pair
    (where gap >= 3 points) and records the dimensions driving the difference.

    Wraps sensitivity.find_high_variance_pairs.

    Columns:
      annex_iii_area, low_case_id, low_case_name, low_csi,
      high_case_id, high_case_name, high_csi, csi_difference,
      differing_dimensions, interpretation, dataset_version
    """
    result = find_high_variance_pairs(df)
    if not result.empty:
        result = result.copy()
        result["dataset_version"] = DATASET_VERSION
    return result


# ── All tables ─────────────────────────────────────────────────────────────────


def compute_all_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Compute all 7 analysis tables from a scored DataFrame.

    Returns a dict with keys matching the manuscript table names:
      table_1_csalite_dimensions
      table_2_corpus_composition_by_annex_area
      table_3_within_category_variance
      table_4_dimension_level_patterns
      table_5_evidence_confidence_by_dimension
      table_6_sensitivity_summary
      table_7_matched_case_contrasts

    Table 1 does not require a DataFrame (framework metadata).
    All other tables require a scored DataFrame with context_severity_* columns.
    """
    return {
        "table_1_csalite_dimensions": table_1_csalite_dimensions(),
        "table_2_corpus_composition_by_annex_area": table_2_corpus_composition_by_annex_area(df),
        "table_3_within_category_variance": table_3_within_category_variance(df),
        "table_4_dimension_level_patterns": table_4_dimension_level_patterns(df),
        "table_5_evidence_confidence_by_dimension": table_5_evidence_confidence_by_dimension(df),
        "table_6_sensitivity_summary": table_6_sensitivity_summary(df),
        "table_7_matched_case_contrasts": table_7_matched_case_contrasts(df),
    }

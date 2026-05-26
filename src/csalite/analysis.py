"""
Analysis table generation for CSA-lite manuscript.

Produces the 7 analysis tables described in the manuscript.
All functions return DataFrames sorted deterministically.
No I/O — callers handle reading/writing via io.py.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from csalite.constants import CONFIDENCE_WEIGHTS, SCORE_DIMENSIONS
from csalite.enums import SeverityBand
from csalite.sensitivity import compute_sensitivity_dataframe, find_high_variance_pairs


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


def table_1_corpus_composition(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 1: Corpus composition by Annex III area.

    Columns:
      annex_iii_area, n_cases, n_direct, n_analogous, n_comparator, n_unclear,
      n_countries, most_common_deployer_type, median_source_quality,
      median_evidence_completeness
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "annex_iii_area", "n_cases", "n_direct", "n_analogous",
                "n_comparator", "n_unclear", "n_countries",
                "most_common_deployer_type", "median_source_quality",
                "median_evidence_completeness",
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
            }
        )

    return pd.DataFrame(rows).sort_values("annex_iii_area").reset_index(drop=True)


# ── Table 2 ────────────────────────────────────────────────────────────────────


def table_2_within_category_variance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 2: Within-category CSI variance.

    Columns:
      annex_iii_area, n_cases, min, q1, median, q3, max, iqr, mean, std,
      n_low, n_moderate, n_high, n_severe, n_high_or_severe,
      variance_interpretation
    """
    if df.empty or "context_severity_index" not in df.columns:
        return pd.DataFrame(
            columns=[
                "annex_iii_area", "n_cases", "min", "q1", "median", "q3", "max",
                "iqr", "mean", "std", "n_low", "n_moderate", "n_high", "n_severe",
                "n_high_or_severe", "variance_interpretation",
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
            row = {
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
            }
        )
        rows.append(row)

    return pd.DataFrame(rows).sort_values("annex_iii_area").reset_index(drop=True)


# ── Table 3 ────────────────────────────────────────────────────────────────────


def table_3_dimension_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 3: Dimension-level scoring patterns.

    Columns:
      dimension, mean_score, median_score, n_score_0, n_score_1, n_score_2,
      n_missing, missingness_rate, high_score_rate, mean_confidence_weight
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "dimension", "mean_score", "median_score",
                "n_score_0", "n_score_1", "n_score_2",
                "n_missing", "missingness_rate", "high_score_rate",
                "mean_confidence_weight",
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
            }
        )

    return pd.DataFrame(rows)


# ── Table 4 ────────────────────────────────────────────────────────────────────


def table_4_missingness_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 4: Missingness by annex area and dimension.

    Columns:
      annex_iii_area, dimension, n_cases, n_missing, missingness_rate,
      n_low_confidence, low_confidence_rate
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "annex_iii_area", "dimension", "n_cases", "n_missing",
                "missingness_rate", "n_low_confidence", "low_confidence_rate",
            ]
        )

    rows = []
    for area, group in df.groupby("annex_iii_area"):
        n_cases = len(group)
        for dim in SCORE_DIMENSIONS:
            score_col = f"{dim}_score"
            conf_col = f"{dim}_confidence"

            scores = pd.to_numeric(group.get(score_col, pd.Series(dtype=float)), errors="coerce")
            n_missing = int(scores.isna().sum())

            confs = group.get(conf_col, pd.Series(dtype=str)).fillna("unknown")
            n_low_conf = int((confs == "low").sum())

            rows.append(
                {
                    "annex_iii_area": area,
                    "dimension": dim,
                    "n_cases": n_cases,
                    "n_missing": n_missing,
                    "missingness_rate": round(n_missing / n_cases, 4) if n_cases > 0 else None,
                    "n_low_confidence": n_low_conf,
                    "low_confidence_rate": round(n_low_conf / n_cases, 4) if n_cases > 0 else None,
                }
            )

    return (
        pd.DataFrame(rows)
        .sort_values(["annex_iii_area", "dimension"])
        .reset_index(drop=True)
    )


# ── Table 5 ────────────────────────────────────────────────────────────────────


def table_5_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 5: Sensitivity analysis per case.

    Columns per spec (wraps sensitivity.compute_sensitivity_dataframe and adds ECI).
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "case_id", "case_name", "annex_iii_area",
                "unknown_as_zero_score", "unknown_as_zero_band",
                "unknown_as_neutral_score", "unknown_as_neutral_band",
                "unknown_as_conservative_score", "unknown_as_conservative_band",
                "sensitivity_band_change", "missing_dimensions_count",
                "evidence_completeness_index",
            ]
        )

    sens = compute_sensitivity_dataframe(df)

    if "evidence_completeness_index" in df.columns:
        eci_map = df.set_index("case_id")["evidence_completeness_index"].to_dict()
        sens["evidence_completeness_index"] = sens["case_id"].map(eci_map)
    else:
        sens["evidence_completeness_index"] = None

    return sens.sort_values("case_id").reset_index(drop=True)


# ── Table 6 ────────────────────────────────────────────────────────────────────


def table_6_high_variance_pairs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 6: High-variance within-category case pairs.
    Delegates to sensitivity.find_high_variance_pairs.
    """
    return find_high_variance_pairs(df)


# ── Table 7 ────────────────────────────────────────────────────────────────────


def table_7_review_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 7: Cases requiring review.

    Columns:
      case_id, case_name, annex_iii_area, context_severity_index,
      context_severity_band, missing_dimensions_count, evidence_completeness_index,
      source_quality_score, high_missingness_flag, low_source_quality_flag,
      sensitivity_band_change, review_required_flag, review_reason
    """
    required_cols = {"review_required_flag"}
    if df.empty or not required_cols.issubset(df.columns):
        return pd.DataFrame(
            columns=[
                "case_id", "case_name", "annex_iii_area",
                "context_severity_index", "context_severity_band",
                "missing_dimensions_count", "evidence_completeness_index",
                "source_quality_score", "high_missingness_flag",
                "low_source_quality_flag", "sensitivity_band_change",
                "review_required_flag", "review_reason",
            ]
        )

    flagged = df[df["review_required_flag"] == True].copy()  # noqa: E712

    cols = [
        "case_id", "case_name", "annex_iii_area",
        "context_severity_index", "context_severity_band",
        "missing_dimensions_count", "evidence_completeness_index",
        "source_quality_score", "high_missingness_flag",
        "low_source_quality_flag", "sensitivity_band_change",
        "review_required_flag",
    ]
    # Only include columns that exist
    cols = [c for c in cols if c in flagged.columns]
    flagged = flagged[cols].copy()

    def _reason(row: pd.Series) -> str:
        reasons = []
        if row.get("high_missingness_flag"):
            reasons.append("high missingness")
        if row.get("low_source_quality_flag"):
            reasons.append("low source quality")
        if row.get("sensitivity_band_change"):
            reasons.append("sensitivity band change")
        band = row.get("context_severity_band", "")
        eci = row.get("evidence_completeness_index", 1.0)
        if band in ("high", "severe") and (eci is not None and eci < 0.5):
            reasons.append(f"high/severe band with low ECI ({eci:.2f})")
        return "; ".join(reasons) if reasons else "unknown"

    flagged["review_reason"] = flagged.apply(_reason, axis=1)
    return flagged.sort_values("case_id").reset_index(drop=True)


# ── All tables ─────────────────────────────────────────────────────────────────


def compute_all_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Compute all 7 analysis tables from a scored DataFrame.

    Returns a dict with keys:
      table_1_corpus_composition
      table_2_within_category_variance
      table_3_dimension_patterns
      table_4_missingness_by_category
      table_5_sensitivity
      table_6_high_variance_case_pairs
      table_7_review_flags
    """
    return {
        "table_1_corpus_composition": table_1_corpus_composition(df),
        "table_2_within_category_variance": table_2_within_category_variance(df),
        "table_3_dimension_patterns": table_3_dimension_patterns(df),
        "table_4_missingness_by_category": table_4_missingness_by_category(df),
        "table_5_sensitivity": table_5_sensitivity(df),
        "table_6_high_variance_case_pairs": table_6_high_variance_pairs(df),
        "table_7_review_flags": table_7_review_flags(df),
    }

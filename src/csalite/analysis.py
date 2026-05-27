"""
Analysis table generation for CSA-lite manuscript.

Produces the 8 analysis tables described in the manuscript.
All functions return DataFrames sorted deterministically.
No I/O — callers handle reading/writing via io.py.

Table naming follows the manuscript:
  table_1_csalite_dimensions          — framework metadata (no df needed)
  table_2_source_quality_scale        — source quality scale reference (no df needed)
  table_3_corpus_composition_by_annex_area
  table_4_within_category_variance
  table_5_dimension_level_patterns
  table_6_evidence_confidence_by_dimension
  table_7_sensitivity_summary
  table_8_matched_case_contrasts
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


def table_2_source_quality_scale() -> pd.DataFrame:
    """
    Table 2: Source quality scale reference (framework metadata).

    No DataFrame input — this is a framework-level metadata table.
    Five rows (scores 0–4) with label and definition.

    Columns: Score, Label, Definition
    """
    rows = [
        {"Score": 0, "Label": "Unusable", "Definition": "No usable public record; source absent, paywalled, or removed"},
        {"Score": 1, "Label": "Low", "Definition": "Single low-credibility source; blog, social media, or unverified report"},
        {"Score": 2, "Label": "Medium", "Definition": "One or more credible secondary sources (journalism, NGO, government summary)"},
        {"Score": 3, "Label": "High", "Definition": "Primary documentation (official report, court record, regulator finding, or investigation with methodology)"},
        {"Score": 4, "Label": "Very High", "Definition": "Multiple independent primary sources with full methodology, including regulatory, judicial, or academic peer-reviewed documentation"},
    ]
    return pd.DataFrame(rows)


# ── Table 3 ────────────────────────────────────────────────────────────────────


def table_3_corpus_composition_by_annex_area(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 3: Corpus composition by Annex III area.

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


# ── Table 4 ────────────────────────────────────────────────────────────────────


def table_4_within_category_variance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 4: Within-category CSI variance by Annex III area.

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


# ── Table 5 ────────────────────────────────────────────────────────────────────


def table_5_dimension_level_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 5: Dimension-level scoring patterns across the corpus.

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


# ── Table 6 ────────────────────────────────────────────────────────────────────


def table_6_evidence_confidence_by_dimension(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 6: Evidence confidence distribution by dimension.

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


# ── Table 7 ────────────────────────────────────────────────────────────────────


def table_7_sensitivity_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 7: Sensitivity analysis summary by Annex III area.

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


# ── Table 8 ────────────────────────────────────────────────────────────────────


def table_8_matched_case_contrasts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Table 8: Matched case contrasts within Annex III areas.

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


# ── Supplementary Tables ───────────────────────────────────────────────────────


def supp_table_s1_full_case_corpus(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supplementary Table S1: Full case corpus with all fields.

    All 45 cases, all coded columns, no truncation.
    Adds dataset_version column.
    """
    result = df.copy()
    result["dataset_version"] = DATASET_VERSION
    return result.reset_index(drop=True)


def supp_table_s2_scored_cases(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supplementary Table S2: Scored cases with all scoring columns.

    If context_severity_index is not present (unscored df), scores first.
    """
    if "context_severity_index" not in df.columns:
        from csalite.scoring import score_dataframe
        df = score_dataframe(df)
    result = df.copy()
    result["dataset_version"] = DATASET_VERSION
    return result.reset_index(drop=True)


def supp_table_s3_sensitivity_per_case(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supplementary Table S3: Per-case sensitivity analysis.

    Columns: case_id, case_name, csi_neutral, csi_zero, csi_conservative,
    band_neutral, band_zero, band_conservative, sensitivity_band_change.
    """
    from csalite.sensitivity import compute_sensitivity_dataframe

    if "context_severity_index" not in df.columns:
        from csalite.scoring import score_dataframe
        df = score_dataframe(df)

    sens = compute_sensitivity_dataframe(df)

    rename_map = {
        "context_severity_index": "csi_neutral",
        "unknown_as_zero_score": "csi_zero",
        "unknown_as_neutral_score": "csi_neutral_check",
        "unknown_as_conservative_score": "csi_conservative",
        "context_severity_band": "band_neutral",
        "unknown_as_zero_band": "band_zero",
        "unknown_as_neutral_band": "band_neutral_check",
        "unknown_as_conservative_band": "band_conservative",
    }

    priority_cols = ["case_id", "case_name"] + list(rename_map.keys()) + ["sensitivity_band_change"]
    available = [c for c in priority_cols if c in sens.columns]
    result = sens[available].rename(columns=rename_map).copy()
    result["dataset_version"] = DATASET_VERSION
    return result.reset_index(drop=True)


def supp_table_s4_sources_manifest(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supplementary Table S4: Sources manifest.

    One row per case; extracts source fields and quality metadata.
    """
    cols = [
        "case_id", "case_name", "source_repository",
        "primary_sources", "secondary_sources",
        "source_quality_score", "source_quality_rationale",
        "last_verified_date",
    ]
    available = [c for c in cols if c in df.columns]
    result = df[available].copy()
    result["dataset_version"] = DATASET_VERSION
    return result.reset_index(drop=True)


def supp_table_s5_annex_mapping_rationales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supplementary Table S5: Annex III mapping rationales.

    One row per case; captures the mapping classification evidence.
    """
    cols = [
        "case_id", "case_name",
        "annex_iii_area", "annex_iii_subcategory",
        "annex_mapping_type", "annex_mapping_confidence",
        "annex_mapping_rationale", "eu_scope_note",
    ]
    available = [c for c in cols if c in df.columns]
    result = df[available].copy()
    result["dataset_version"] = DATASET_VERSION
    return result.reset_index(drop=True)


def supp_table_s6_validation_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supplementary Table S6: Validation summary — per-case rule check results.

    Runs validate_dataframe and summarises per-case issues.
    """
    from csalite.validation import validate_dataframe

    val_result = validate_dataframe(df)

    case_errors: dict[str, int] = {}
    case_warnings: dict[str, int] = {}
    for issue in val_result.errors:
        case_errors[issue.case_id] = case_errors.get(issue.case_id, 0) + 1
    for issue in val_result.warnings:
        case_warnings[issue.case_id] = case_warnings.get(issue.case_id, 0) + 1

    rows = []
    for _, row in df.iterrows():
        cid = str(row.get("case_id", ""))
        rows.append({
            "case_id": cid,
            "case_name": str(row.get("case_name", "")),
            "n_errors": case_errors.get(cid, 0),
            "n_warnings": case_warnings.get(cid, 0),
            "validation_status": "pass" if case_errors.get(cid, 0) == 0 else "fail",
            "dataset_version": DATASET_VERSION,
        })

    summary_row = {
        "case_id": "__CORPUS__",
        "case_name": f"All {len(df)} cases",
        "n_errors": len(val_result.errors),
        "n_warnings": len(val_result.warnings),
        "validation_status": "pass" if val_result.is_valid else "fail",
        "dataset_version": DATASET_VERSION,
    }
    return pd.DataFrame([summary_row] + rows)


def supp_table_s7_case_audit_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supplementary Table S7: Case audit flags.

    For each case, reports per-case quality and completeness flags.
    Classifies issues as blocking / major / minor / informational.
    """
    from csalite.constants import SCORE_DIMENSIONS

    if "context_severity_index" not in df.columns:
        from csalite.scoring import score_dataframe
        df = score_dataframe(df)

    rows = []
    for _, row in df.iterrows():
        cid = str(row.get("case_id", ""))
        cname = str(row.get("case_name", ""))

        n_coded = 0
        n_missing = 0
        for dim in SCORE_DIMENSIONS:
            val = row.get(f"{dim}_score", None)
            if val is None or (isinstance(val, float) and math.isnan(val)):
                n_missing += 1
            else:
                n_coded += 1

        sq = row.get("source_quality_score", None)
        try:
            sq_int = int(sq) if sq is not None else None
        except (ValueError, TypeError):
            sq_int = None
        low_sq = (sq_int is not None and sq_int <= 1)

        ps = str(row.get("primary_sources", "")).strip()
        no_primary = (ps == "" or ps.lower() in ("nan", "n/a", "none"))

        mr = str(row.get("annex_mapping_rationale", "")).strip()
        no_mapping_rationale = (mr == "" or mr.lower() in ("nan", "n/a", "none"))

        flags = []
        if n_missing > 0:
            flags.append(f"missing_dimensions:{n_missing}")
        if low_sq:
            flags.append("low_source_quality")
        if no_primary:
            flags.append("no_primary_source")
        if no_mapping_rationale:
            flags.append("no_mapping_rationale")
        if row.get("high_missingness_flag", False):
            flags.append("high_missingness_flag")
        if row.get("sensitivity_band_change", False):
            flags.append("sensitivity_band_change")

        severity = "informational"
        if no_primary or n_missing == len(SCORE_DIMENSIONS):
            severity = "blocking"
        elif low_sq or no_mapping_rationale:
            severity = "major"
        elif n_missing > 0:
            severity = "minor"

        rows.append({
            "case_id": cid,
            "case_name": cname,
            "n_dimensions_coded": n_coded,
            "n_dimensions_missing": n_missing,
            "source_quality_score": sq_int,
            "low_source_quality_flag": low_sq,
            "no_primary_source_flag": no_primary,
            "no_mapping_rationale_flag": no_mapping_rationale,
            "high_missingness_flag": bool(row.get("high_missingness_flag", False)),
            "sensitivity_band_change_flag": bool(row.get("sensitivity_band_change", False)),
            "audit_flags": "; ".join(flags) if flags else "none",
            "audit_severity": severity,
            "dataset_version": DATASET_VERSION,
        })

    return pd.DataFrame(rows)


def compute_all_supplementary_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Compute all 7 supplementary tables from a (optionally scored) DataFrame.

    Returns a dict keyed by supplementary table names:
      supp_table_s1_full_case_corpus
      supp_table_s2_scored_cases
      supp_table_s3_sensitivity_per_case
      supp_table_s4_sources_manifest
      supp_table_s5_annex_mapping_rationales
      supp_table_s6_validation_summary
      supp_table_s7_case_audit_flags
    """
    if "context_severity_index" not in df.columns:
        from csalite.scoring import score_dataframe
        df = score_dataframe(df)

    return {
        "supp_table_s1_full_case_corpus": supp_table_s1_full_case_corpus(df),
        "supp_table_s2_scored_cases": supp_table_s2_scored_cases(df),
        "supp_table_s3_sensitivity_per_case": supp_table_s3_sensitivity_per_case(df),
        "supp_table_s4_sources_manifest": supp_table_s4_sources_manifest(df),
        "supp_table_s5_annex_mapping_rationales": supp_table_s5_annex_mapping_rationales(df),
        "supp_table_s6_validation_summary": supp_table_s6_validation_summary(df),
        "supp_table_s7_case_audit_flags": supp_table_s7_case_audit_flags(df),
    }


# ── All tables ─────────────────────────────────────────────────────────────────


def compute_all_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Compute all 8 analysis tables from a scored DataFrame.

    Returns a dict with keys matching the manuscript table names:
      table_1_csalite_dimensions
      table_2_source_quality_scale
      table_3_corpus_composition_by_annex_area
      table_4_within_category_variance
      table_5_dimension_level_patterns
      table_6_evidence_confidence_by_dimension
      table_7_sensitivity_summary
      table_8_matched_case_contrasts

    Tables 1 and 2 do not require a DataFrame (framework metadata).
    All other tables require a scored DataFrame with context_severity_* columns.
    """
    return {
        "table_1_csalite_dimensions": table_1_csalite_dimensions(),
        "table_2_source_quality_scale": table_2_source_quality_scale(),
        "table_3_corpus_composition_by_annex_area": table_3_corpus_composition_by_annex_area(df),
        "table_4_within_category_variance": table_4_within_category_variance(df),
        "table_5_dimension_level_patterns": table_5_dimension_level_patterns(df),
        "table_6_evidence_confidence_by_dimension": table_6_evidence_confidence_by_dimension(df),
        "table_7_sensitivity_summary": table_7_sensitivity_summary(df),
        "table_8_matched_case_contrasts": table_8_matched_case_contrasts(df),
    }

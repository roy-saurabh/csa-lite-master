"""
Sensitivity analysis for CSA-lite scores.

Computes the effect of different imputation assumptions for null scores
(zero, neutral, conservative) and identifies cases where the band assignment
changes across assumptions.

All functions are pure — no I/O, no side effects.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from csalite.constants import SCORE_DIMENSIONS
from csalite.enums import SeverityBand
from csalite.scoring import (
    compute_csi_conservative,
    compute_csi_neutral,
    compute_csi_zero,
    compute_dimension_scores,
    score_to_band,
)


def compute_sensitivity_row(row: pd.Series | dict[str, Any]) -> dict[str, Any]:
    """
    Compute sensitivity fields for a single case row.

    Returns a dict with all three imputation variants and their bands,
    plus whether the band changed.
    """
    if isinstance(row, pd.Series):
        row = row.to_dict()

    scores = compute_dimension_scores(row)

    csi_zero = compute_csi_zero(scores)
    csi_neutral = compute_csi_neutral(scores)
    csi_conservative = compute_csi_conservative(scores)

    band_zero = score_to_band(csi_zero)
    band_neutral = score_to_band(csi_neutral)
    band_conservative = score_to_band(csi_conservative)

    known_bands = {b for b in (band_zero, band_neutral, band_conservative) if b != SeverityBand.unknown}
    sensitivity_band_change = len(known_bands) > 1

    return {
        "case_id": row.get("case_id", ""),
        "case_name": row.get("case_name", ""),
        "annex_iii_area": row.get("annex_iii_area", ""),
        "unknown_as_zero_score": csi_zero,
        "unknown_as_zero_band": band_zero.value,
        "unknown_as_neutral_score": csi_neutral,
        "unknown_as_neutral_band": band_neutral.value,
        "unknown_as_conservative_score": csi_conservative,
        "unknown_as_conservative_band": band_conservative.value,
        "sensitivity_band_change": sensitivity_band_change,
        "missing_dimensions_count": sum(1 for v in scores.values() if v is None),
    }


def compute_sensitivity_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute sensitivity analysis for all cases.

    Returns a new DataFrame sorted by case_id with one row per case.
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "case_id", "case_name", "annex_iii_area",
                "unknown_as_zero_score", "unknown_as_zero_band",
                "unknown_as_neutral_score", "unknown_as_neutral_band",
                "unknown_as_conservative_score", "unknown_as_conservative_band",
                "sensitivity_band_change", "missing_dimensions_count",
            ]
        )

    rows = [compute_sensitivity_row(row) for _, row in df.iterrows()]
    result = pd.DataFrame(rows).sort_values("case_id").reset_index(drop=True)
    return result


def compute_band_change_summary(sensitivity_df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarise sensitivity band changes by annex_iii_area.

    Returns a DataFrame with columns:
      annex_iii_area, n_cases, n_band_changes, pct_band_changes
    """
    if sensitivity_df.empty:
        return pd.DataFrame(
            columns=["annex_iii_area", "n_cases", "n_band_changes", "pct_band_changes"]
        )

    summary = (
        sensitivity_df.groupby("annex_iii_area")
        .agg(
            n_cases=("case_id", "count"),
            n_band_changes=("sensitivity_band_change", "sum"),
        )
        .reset_index()
    )
    summary["pct_band_changes"] = (
        summary["n_band_changes"] / summary["n_cases"] * 100
    ).round(1)
    return summary.sort_values("annex_iii_area").reset_index(drop=True)


def find_high_variance_pairs(
    scored_df: pd.DataFrame,
    min_csi_diff: int = 3,
) -> pd.DataFrame:
    """
    Find within-category pairs with high CSI variance (for Table 6).

    For each annex_iii_area, finds the pair of cases with the greatest
    difference in context_severity_index (neutral assumption).

    Parameters
    ----------
    scored_df: DataFrame with scoring columns already computed
    min_csi_diff: minimum CSI difference to include in output

    Returns
    -------
    DataFrame with columns as per Table 6 spec.
    """
    required_cols = {"case_id", "case_name", "annex_iii_area", "context_severity_index"}
    missing = required_cols - set(scored_df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if scored_df.empty:
        return pd.DataFrame(
            columns=[
                "annex_iii_area",
                "low_case_id", "low_case_name", "low_csi",
                "high_case_id", "high_case_name", "high_csi",
                "csi_difference",
                "differing_dimensions",
                "interpretation",
            ]
        )

    rows = []
    for area, group in scored_df.groupby("annex_iii_area"):
        group = group.dropna(subset=["context_severity_index"])
        if len(group) < 2:
            continue

        low_row = group.loc[group["context_severity_index"].idxmin()]
        high_row = group.loc[group["context_severity_index"].idxmax()]
        diff = int(high_row["context_severity_index"]) - int(low_row["context_severity_index"])

        if diff < min_csi_diff:
            continue

        # Identify differing dimensions (score differs between the two)
        differing = []
        for dim in SCORE_DIMENSIONS:
            col = f"{dim}_score"
            lo_val = low_row.get(col)
            hi_val = high_row.get(col)
            if lo_val != hi_val:
                differing.append(dim)

        rows.append(
            {
                "annex_iii_area": area,
                "low_case_id": low_row["case_id"],
                "low_case_name": low_row["case_name"],
                "low_csi": int(low_row["context_severity_index"]),
                "high_case_id": high_row["case_id"],
                "high_case_name": high_row["case_name"],
                "high_csi": int(high_row["context_severity_index"]),
                "csi_difference": diff,
                "differing_dimensions": "; ".join(differing),
                "interpretation": (
                    f"Within {area}, CSI ranges from {int(low_row['context_severity_index'])} "
                    f"to {int(high_row['context_severity_index'])} "
                    f"(diff={diff}), driven by: {', '.join(differing) or 'all dimensions similar'}"
                ),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "annex_iii_area",
                "low_case_id", "low_case_name", "low_csi",
                "high_case_id", "high_case_name", "high_csi",
                "csi_difference",
                "differing_dimensions",
                "interpretation",
            ]
        )

    return pd.DataFrame(rows).sort_values(["annex_iii_area", "csi_difference"], ascending=[True, False]).reset_index(drop=True)

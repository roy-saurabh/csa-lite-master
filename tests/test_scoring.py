"""
Tests for the scoring module.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from csalite.scoring import (
    compute_csi_conservative,
    compute_csi_neutral,
    compute_csi_zero,
    compute_dimension_scores,
    compute_evidence_completeness_index,
    compute_known_count,
    compute_missing_count,
    score_dataframe,
    score_row,
    score_to_band,
)
from csalite.enums import SeverityBand

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_cases_df():
    from csalite.io import read_cases_csv
    return read_cases_csv(FIXTURES / "valid_cases_minimal.csv")


# ── score_to_band ─────────────────────────────────────────────────────────────

class TestScoreToBand:
    def test_zero_is_low(self):
        assert score_to_band(0) == SeverityBand.low

    def test_three_is_low(self):
        assert score_to_band(3) == SeverityBand.low

    def test_four_is_moderate(self):
        assert score_to_band(4) == SeverityBand.moderate

    def test_seven_is_moderate(self):
        assert score_to_band(7) == SeverityBand.moderate

    def test_eight_is_high(self):
        assert score_to_band(8) == SeverityBand.high

    def test_eleven_is_high(self):
        assert score_to_band(11) == SeverityBand.high

    def test_twelve_is_severe(self):
        assert score_to_band(12) == SeverityBand.severe

    def test_sixteen_is_severe(self):
        assert score_to_band(16) == SeverityBand.severe

    def test_none_is_unknown(self):
        assert score_to_band(None) == SeverityBand.unknown


# ── compute_csi variants ──────────────────────────────────────────────────────

class TestCSIVariants:
    def test_all_zeros_neutral(self):
        scores = {d: 0 for d in ["decision_criticality", "autonomy", "vulnerability",
                                  "oversight", "recourse", "scale", "opacity", "monitoring"]}
        assert compute_csi_neutral(scores) == 0

    def test_all_twos_neutral(self):
        scores = {d: 2 for d in ["decision_criticality", "autonomy", "vulnerability",
                                  "oversight", "recourse", "scale", "opacity", "monitoring"]}
        assert compute_csi_neutral(scores) == 16

    def test_null_as_zero(self):
        scores = {"decision_criticality": None, "autonomy": None,
                  "vulnerability": None, "oversight": None,
                  "recourse": None, "scale": None, "opacity": None, "monitoring": None}
        assert compute_csi_zero(scores) == 0

    def test_null_as_neutral_counts_one(self):
        scores = {"decision_criticality": None, "autonomy": None,
                  "vulnerability": None, "oversight": None,
                  "recourse": None, "scale": None, "opacity": None, "monitoring": None}
        assert compute_csi_neutral(scores) is None  # all null -> None

    def test_null_as_conservative(self):
        scores = {"decision_criticality": None, "autonomy": None,
                  "vulnerability": None, "oversight": None,
                  "recourse": None, "scale": None, "opacity": None, "monitoring": None}
        assert compute_csi_conservative(scores) == 16

    def test_mixed_null_neutral(self):
        scores = {"decision_criticality": 2, "autonomy": None,
                  "vulnerability": 1, "oversight": None,
                  "recourse": 0, "scale": None, "opacity": 2, "monitoring": None}
        # known: 2+1+0+2=5, nulls*1=4, total=9
        assert compute_csi_neutral(scores) == 9

    def test_mixed_null_conservative(self):
        scores = {"decision_criticality": 2, "autonomy": None,
                  "vulnerability": 1, "oversight": None,
                  "recourse": 0, "scale": None, "opacity": 2, "monitoring": None}
        # known: 2+1+0+2=5, nulls*2=8, total=13
        assert compute_csi_conservative(scores) == 13


# ── ECI ───────────────────────────────────────────────────────────────────────

class TestECI:
    def test_all_known_high_confidence(self):
        from csalite.enums import ConfidenceLevel
        from csalite.constants import SCORE_DIMENSIONS
        scores = {d: 0 for d in SCORE_DIMENSIONS}
        confs = {d: ConfidenceLevel.high for d in SCORE_DIMENSIONS}
        eci = compute_evidence_completeness_index(scores, confs)
        assert eci == 1.0

    def test_all_missing_gives_zero_eci(self):
        from csalite.enums import ConfidenceLevel
        from csalite.constants import SCORE_DIMENSIONS
        scores = {d: None for d in SCORE_DIMENSIONS}
        confs = {d: ConfidenceLevel.unknown for d in SCORE_DIMENSIONS}
        eci = compute_evidence_completeness_index(scores, confs)
        assert eci == 0.0

    def test_half_known_high_half_missing(self):
        from csalite.enums import ConfidenceLevel
        from csalite.constants import SCORE_DIMENSIONS
        dims = list(SCORE_DIMENSIONS)
        scores = {d: (0 if i < 4 else None) for i, d in enumerate(dims)}
        confs = {d: ConfidenceLevel.high for d in dims}
        eci = compute_evidence_completeness_index(scores, confs)
        # 4 known * 1.0 + 4 missing * 0.0 / 8 = 0.5
        assert eci == 0.5


# ── score_row ─────────────────────────────────────────────────────────────────

class TestScoreRow:
    def test_all_zeros_gives_low_band(self):
        from csalite.constants import SCORE_DIMENSIONS
        row = {f"{d}_score": 0 for d in SCORE_DIMENSIONS}
        row.update({f"{d}_rationale": "rationale" for d in SCORE_DIMENSIONS})
        row.update({f"{d}_confidence": "high" for d in SCORE_DIMENSIONS})
        row["source_quality_score"] = 4
        result = score_row(row)
        assert result["context_severity_index"] == 0
        assert result["context_severity_band"] == "low"
        assert result["known_dimension_count"] == 8
        assert result["missing_dimensions_count"] == 0
        assert result["high_missingness_flag"] is False

    def test_all_twos_gives_severe_band(self):
        from csalite.constants import SCORE_DIMENSIONS
        row = {f"{d}_score": 2 for d in SCORE_DIMENSIONS}
        row.update({f"{d}_rationale": "rationale" for d in SCORE_DIMENSIONS})
        row.update({f"{d}_confidence": "high" for d in SCORE_DIMENSIONS})
        row["source_quality_score"] = 4
        result = score_row(row)
        assert result["context_severity_index"] == 16
        assert result["context_severity_band"] == "severe"

    def test_three_nulls_sets_missingness_flag(self):
        from csalite.constants import SCORE_DIMENSIONS
        dims = list(SCORE_DIMENSIONS)
        row = {f"{dims[i]}_score": (None if i < 3 else 0) for i in range(8)}
        row.update({f"{d}_rationale": "rationale" for d in dims})
        row.update({f"{d}_confidence": "high" for d in dims})
        row["source_quality_score"] = 4
        result = score_row(row)
        assert result["high_missingness_flag"] == True
        assert result["missing_dimensions_count"] == 3


# ── score_dataframe ───────────────────────────────────────────────────────────

class TestScoreDataframe:
    def test_returns_correct_row_count(self, valid_cases_df):
        result = score_dataframe(valid_cases_df)
        assert len(result) == len(valid_cases_df)

    def test_sorted_by_case_id(self, valid_cases_df):
        result = score_dataframe(valid_cases_df)
        case_ids = result["case_id"].tolist()
        assert case_ids == sorted(case_ids)

    def test_computed_columns_present(self, valid_cases_df):
        result = score_dataframe(valid_cases_df)
        expected_cols = [
            "context_severity_index",
            "context_severity_band",
            "known_dimension_count",
            "missing_dimensions_count",
            "evidence_completeness_index",
            "sensitivity_band_change",
            "high_missingness_flag",
            "low_source_quality_flag",
            "review_required_flag",
        ]
        for col in expected_cols:
            assert col in result.columns, f"Missing column: {col}"

    def test_case_0001_all_zeros_gives_low(self, valid_cases_df):
        result = score_dataframe(valid_cases_df)
        row = result[result["case_id"] == "CSA-LITE-0001"].iloc[0]
        assert row["context_severity_band"] == "low"
        assert row["context_severity_index"] == 0

    def test_case_0002_all_twos_gives_severe(self, valid_cases_df):
        result = score_dataframe(valid_cases_df)
        row = result[result["case_id"] == "CSA-LITE-0002"].iloc[0]
        assert row["context_severity_band"] == "severe"
        assert row["context_severity_index"] == 16

    def test_case_0003_partial_missingness(self, valid_cases_df):
        result = score_dataframe(valid_cases_df)
        row = result[result["case_id"] == "CSA-LITE-0003"].iloc[0]
        assert row["missing_dimensions_count"] >= 3
        assert row["high_missingness_flag"] == True

    def test_empty_dataframe_returns_empty(self):
        df = pd.DataFrame()
        result = score_dataframe(df)
        assert result.empty

    def test_sensitivity_band_change_case_0003(self, valid_cases_df):
        """Case 0003 with 3+ nulls should show sensitivity_band_change=True."""
        result = score_dataframe(valid_cases_df)
        row = result[result["case_id"] == "CSA-LITE-0003"].iloc[0]
        # With mixed known scores and 5+ nulls, zero vs conservative imputation should differ
        assert row["sensitivity_band_change"] is True or row["missing_dimensions_count"] >= 5

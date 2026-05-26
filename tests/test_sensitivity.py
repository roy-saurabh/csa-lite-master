"""
Tests for the sensitivity analysis module.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from csalite.sensitivity import (
    compute_band_change_summary,
    compute_sensitivity_dataframe,
    compute_sensitivity_row,
    find_high_variance_pairs,
)
from csalite.scoring import score_dataframe

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_cases_df():
    from csalite.io import read_cases_csv
    return read_cases_csv(FIXTURES / "valid_cases_minimal.csv")


@pytest.fixture
def scored_df(valid_cases_df):
    return score_dataframe(valid_cases_df)


class TestComputeSensitivityRow:
    def test_all_zeros_has_no_band_change(self):
        from csalite.constants import SCORE_DIMENSIONS
        row = {f"{d}_score": 0 for d in SCORE_DIMENSIONS}
        row["case_id"] = "CSA-LITE-0001"
        row["case_name"] = "Test"
        row["annex_iii_area"] = "education_vocational_training"
        result = compute_sensitivity_row(row)
        # 0+0+0=0 across all assumptions => same band
        assert result["sensitivity_band_change"] == False
        assert result["unknown_as_zero_band"] == result["unknown_as_neutral_band"]
        assert result["unknown_as_neutral_band"] == result["unknown_as_conservative_band"]

    def test_all_nulls_zero_vs_conservative_differ(self):
        from csalite.constants import SCORE_DIMENSIONS
        row = {f"{d}_score": None for d in SCORE_DIMENSIONS}
        row["case_id"] = "CSA-LITE-0003"
        row["case_name"] = "Border"
        row["annex_iii_area"] = "migration_asylum_border_control"
        result = compute_sensitivity_row(row)
        # zero: 0->low, conservative: 16->severe -> band changes
        assert result["unknown_as_zero_band"] == "low"
        assert result["unknown_as_conservative_band"] == "severe"
        assert result["sensitivity_band_change"] is True

    def test_contains_required_keys(self):
        from csalite.constants import SCORE_DIMENSIONS
        row = {f"{d}_score": 1 for d in SCORE_DIMENSIONS}
        row["case_id"] = "CSA-LITE-0001"
        row["case_name"] = "Test"
        row["annex_iii_area"] = "education_vocational_training"
        result = compute_sensitivity_row(row)
        required_keys = [
            "case_id", "case_name", "annex_iii_area",
            "unknown_as_zero_score", "unknown_as_zero_band",
            "unknown_as_neutral_score", "unknown_as_neutral_band",
            "unknown_as_conservative_score", "unknown_as_conservative_band",
            "sensitivity_band_change", "missing_dimensions_count",
        ]
        for k in required_keys:
            assert k in result, f"Missing key: {k}"


class TestComputeSensitivityDataframe:
    def test_returns_correct_row_count(self, valid_cases_df):
        result = compute_sensitivity_dataframe(valid_cases_df)
        assert len(result) == len(valid_cases_df)

    def test_sorted_by_case_id(self, valid_cases_df):
        result = compute_sensitivity_dataframe(valid_cases_df)
        ids = result["case_id"].tolist()
        assert ids == sorted(ids)

    def test_empty_returns_empty_with_columns(self):
        result = compute_sensitivity_dataframe(pd.DataFrame())
        assert result.empty
        assert "case_id" in result.columns

    def test_case_0003_shows_band_change(self, valid_cases_df):
        result = compute_sensitivity_dataframe(valid_cases_df)
        row = result[result["case_id"] == "CSA-LITE-0003"].iloc[0]
        # 0003 has 5+ null scores so band change expected
        assert row["sensitivity_band_change"] == True


class TestBandChangeSummary:
    def test_returns_aggregated_by_area(self, valid_cases_df):
        sens_df = compute_sensitivity_dataframe(valid_cases_df)
        summary = compute_band_change_summary(sens_df)
        assert "annex_iii_area" in summary.columns
        assert "n_cases" in summary.columns
        assert "n_band_changes" in summary.columns
        assert "pct_band_changes" in summary.columns

    def test_empty_returns_empty(self):
        result = compute_band_change_summary(pd.DataFrame(
            columns=["annex_iii_area", "case_id", "sensitivity_band_change"]
        ))
        assert result.empty


class TestFindHighVariancePairs:
    def test_returns_dataframe(self, scored_df):
        result = find_high_variance_pairs(scored_df, min_csi_diff=1)
        assert isinstance(result, pd.DataFrame)

    def test_contains_required_columns(self, scored_df):
        result = find_high_variance_pairs(scored_df, min_csi_diff=1)
        if not result.empty:
            for col in ["annex_iii_area", "low_case_id", "high_case_id", "csi_difference"]:
                assert col in result.columns

    def test_high_threshold_returns_fewer_pairs(self, scored_df):
        low_thresh = find_high_variance_pairs(scored_df, min_csi_diff=1)
        high_thresh = find_high_variance_pairs(scored_df, min_csi_diff=20)
        assert len(low_thresh) >= len(high_thresh)

    def test_missing_required_columns_raises(self):
        bad_df = pd.DataFrame({"case_id": ["CSA-LITE-0001"]})
        with pytest.raises(ValueError, match="Missing required columns"):
            find_high_variance_pairs(bad_df)

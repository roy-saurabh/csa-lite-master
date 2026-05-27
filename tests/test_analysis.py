"""
Tests for the analysis module (table generation).

23 tests covering all 8 manuscript tables.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from csalite.analysis import (
    compute_all_tables,
    table_1_csalite_dimensions,
    table_2_source_quality_scale,
    table_3_corpus_composition_by_annex_area,
    table_4_within_category_variance,
    table_5_dimension_level_patterns,
    table_6_evidence_confidence_by_dimension,
    table_7_sensitivity_summary,
    table_8_matched_case_contrasts,
)
from csalite.constants import SCORE_DIMENSIONS
from csalite.scoring import score_dataframe

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_cases_df():
    from csalite.io import read_cases_csv
    return read_cases_csv(FIXTURES / "valid_cases_minimal.csv")


@pytest.fixture
def scored_df(valid_cases_df):
    return score_dataframe(valid_cases_df)


# ── Table 1: CSA-lite dimensions (no df needed) ───────────────────────────────

class TestTable1:
    def test_returns_dataframe(self):
        result = table_1_csalite_dimensions()
        assert isinstance(result, pd.DataFrame)

    def test_has_required_columns(self):
        result = table_1_csalite_dimensions()
        for col in ["dimension", "description", "score_0", "score_1", "score_2",
                    "evidence_required", "missingness_note", "dataset_version"]:
            assert col in result.columns, f"Missing column: {col}"

    def test_has_8_rows(self):
        result = table_1_csalite_dimensions()
        assert len(result) == 8

    def test_all_dimensions_present(self):
        result = table_1_csalite_dimensions()
        assert set(result["dimension"]) == set(SCORE_DIMENSIONS)

    def test_dataset_version_is_0_2_0(self):
        result = table_1_csalite_dimensions()
        assert (result["dataset_version"] == "0.2.0").all()


# ── Table 2: Source quality scale (no df needed) ─────────────────────────────

class TestTable2:
    def test_returns_dataframe(self):
        result = table_2_source_quality_scale()
        assert isinstance(result, pd.DataFrame)

    def test_has_required_columns(self):
        result = table_2_source_quality_scale()
        for col in ["Score", "Label", "Definition"]:
            assert col in result.columns, f"Missing column: {col}"

    def test_has_5_rows(self):
        result = table_2_source_quality_scale()
        assert len(result) == 5

    def test_scores_are_0_to_4(self):
        result = table_2_source_quality_scale()
        assert list(result["Score"]) == [0, 1, 2, 3, 4]

    def test_labels_correct(self):
        result = table_2_source_quality_scale()
        expected_labels = ["Unusable", "Low", "Medium", "High", "Very High"]
        assert list(result["Label"]) == expected_labels


# ── Table 3: Corpus composition by Annex III area ─────────────────────────────

class TestTable3:
    def test_returns_dataframe(self, scored_df):
        result = table_3_corpus_composition_by_annex_area(scored_df)
        assert isinstance(result, pd.DataFrame)

    def test_has_required_columns(self, scored_df):
        result = table_3_corpus_composition_by_annex_area(scored_df)
        required = ["annex_iii_area", "n_cases", "n_direct", "n_analogous",
                    "n_comparator", "n_unclear", "n_countries",
                    "most_common_deployer_type", "median_source_quality"]
        for col in required:
            assert col in result.columns, f"Missing column: {col}"

    def test_correct_case_count(self, scored_df):
        result = table_3_corpus_composition_by_annex_area(scored_df)
        assert result["n_cases"].sum() == len(scored_df)


# ── Table 4: Within-category variance ────────────────────────────────────────

class TestTable4:
    def test_returns_dataframe(self, scored_df):
        result = table_4_within_category_variance(scored_df)
        assert isinstance(result, pd.DataFrame)

    def test_has_variance_columns(self, scored_df):
        result = table_4_within_category_variance(scored_df)
        for col in ["min", "max", "median", "iqr", "mean"]:
            assert col in result.columns

    def test_empty_returns_empty(self):
        result = table_4_within_category_variance(pd.DataFrame())
        assert result.empty


# ── Table 5: Dimension-level patterns ────────────────────────────────────────

class TestTable5:
    def test_returns_8_rows(self, scored_df):
        result = table_5_dimension_level_patterns(scored_df)
        assert len(result) == 8

    def test_has_required_columns(self, scored_df):
        result = table_5_dimension_level_patterns(scored_df)
        for col in ["dimension", "mean_score", "n_missing", "missingness_rate",
                    "mean_confidence_weight"]:
            assert col in result.columns

    def test_missingness_rate_in_range(self, scored_df):
        result = table_5_dimension_level_patterns(scored_df)
        rates = result["missingness_rate"].dropna()
        assert (rates >= 0).all()
        assert (rates <= 1).all()

    def test_empty_returns_empty(self):
        result = table_5_dimension_level_patterns(pd.DataFrame())
        assert result.empty


# ── Table 6: Evidence confidence by dimension ─────────────────────────────────

class TestTable6:
    def test_returns_8_rows(self, scored_df):
        result = table_6_evidence_confidence_by_dimension(scored_df)
        assert len(result) == 8

    def test_has_required_columns(self, scored_df):
        result = table_6_evidence_confidence_by_dimension(scored_df)
        for col in ["dimension", "n_high", "n_medium", "n_low", "n_unknown",
                    "mean_confidence_weight"]:
            assert col in result.columns


# ── Table 7: Sensitivity summary ─────────────────────────────────────────────

class TestTable7:
    def test_returns_dataframe(self, scored_df):
        result = table_7_sensitivity_summary(scored_df)
        assert isinstance(result, pd.DataFrame)

    def test_has_required_columns(self, scored_df):
        result = table_7_sensitivity_summary(scored_df)
        for col in ["annex_iii_area", "n_cases", "n_band_changes", "pct_band_changes"]:
            assert col in result.columns


# ── Table 8: Matched case contrasts ──────────────────────────────────────────

class TestTable8:
    def test_returns_dataframe(self, scored_df):
        result = table_8_matched_case_contrasts(scored_df)
        assert isinstance(result, pd.DataFrame)

    def test_csi_difference_nonnegative_when_nonempty(self, scored_df):
        result = table_8_matched_case_contrasts(scored_df)
        if not result.empty:
            assert (result["csi_difference"] >= 0).all()


# ── compute_all_tables ────────────────────────────────────────────────────────

class TestComputeAllTables:
    def test_returns_8_tables(self, scored_df):
        tables = compute_all_tables(scored_df)
        assert len(tables) == 8

    def test_all_tables_are_dataframes(self, scored_df):
        tables = compute_all_tables(scored_df)
        for name, df in tables.items():
            assert isinstance(df, pd.DataFrame), f"{name} is not a DataFrame"

    def test_table_names_correct(self, scored_df):
        tables = compute_all_tables(scored_df)
        expected = {
            "table_1_csalite_dimensions",
            "table_2_source_quality_scale",
            "table_3_corpus_composition_by_annex_area",
            "table_4_within_category_variance",
            "table_5_dimension_level_patterns",
            "table_6_evidence_confidence_by_dimension",
            "table_7_sensitivity_summary",
            "table_8_matched_case_contrasts",
        }
        assert set(tables.keys()) == expected

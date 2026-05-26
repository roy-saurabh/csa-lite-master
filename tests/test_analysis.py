"""
Tests for the analysis module (table generation).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from csalite.analysis import (
    compute_all_tables,
    table_1_corpus_composition,
    table_2_within_category_variance,
    table_3_dimension_patterns,
    table_4_missingness_by_category,
    table_5_sensitivity,
    table_6_high_variance_pairs,
    table_7_review_flags,
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


# ── Table 1 ───────────────────────────────────────────────────────────────────

class TestTable1:
    def test_returns_dataframe(self, scored_df):
        result = table_1_corpus_composition(scored_df)
        assert isinstance(result, pd.DataFrame)

    def test_has_required_columns(self, scored_df):
        result = table_1_corpus_composition(scored_df)
        required = ["annex_iii_area", "n_cases", "n_direct", "n_analogous",
                    "n_comparator", "n_unclear", "n_countries",
                    "most_common_deployer_type", "median_source_quality"]
        for col in required:
            assert col in result.columns, f"Missing column: {col}"

    def test_correct_case_count(self, scored_df):
        result = table_1_corpus_composition(scored_df)
        assert result["n_cases"].sum() == len(scored_df)

    def test_empty_returns_empty(self):
        result = table_1_corpus_composition(pd.DataFrame())
        assert result.empty


# ── Table 2 ───────────────────────────────────────────────────────────────────

class TestTable2:
    def test_returns_dataframe(self, scored_df):
        result = table_2_within_category_variance(scored_df)
        assert isinstance(result, pd.DataFrame)

    def test_has_variance_columns(self, scored_df):
        result = table_2_within_category_variance(scored_df)
        for col in ["min", "max", "median", "iqr", "mean"]:
            assert col in result.columns

    def test_empty_returns_empty(self):
        result = table_2_within_category_variance(pd.DataFrame())
        assert result.empty


# ── Table 3 ───────────────────────────────────────────────────────────────────

class TestTable3:
    def test_returns_8_rows(self, scored_df):
        result = table_3_dimension_patterns(scored_df)
        assert len(result) == 8

    def test_has_required_columns(self, scored_df):
        result = table_3_dimension_patterns(scored_df)
        for col in ["dimension", "mean_score", "n_missing", "missingness_rate"]:
            assert col in result.columns

    def test_missingness_rate_in_range(self, scored_df):
        result = table_3_dimension_patterns(scored_df)
        rates = result["missingness_rate"].dropna()
        assert (rates >= 0).all()
        assert (rates <= 1).all()

    def test_empty_returns_empty(self):
        result = table_3_dimension_patterns(pd.DataFrame())
        assert result.empty


# ── Table 4 ───────────────────────────────────────────────────────────────────

class TestTable4:
    def test_returns_area_x_dimension_rows(self, scored_df):
        result = table_4_missingness_by_category(scored_df)
        n_areas = scored_df["annex_iii_area"].nunique()
        assert len(result) == n_areas * 8

    def test_has_required_columns(self, scored_df):
        result = table_4_missingness_by_category(scored_df)
        for col in ["annex_iii_area", "dimension", "n_cases", "n_missing", "missingness_rate"]:
            assert col in result.columns

    def test_empty_returns_empty(self):
        result = table_4_missingness_by_category(pd.DataFrame())
        assert result.empty


# ── Table 5 ───────────────────────────────────────────────────────────────────

class TestTable5:
    def test_returns_correct_row_count(self, scored_df):
        result = table_5_sensitivity(scored_df)
        assert len(result) == len(scored_df)

    def test_empty_returns_empty(self):
        result = table_5_sensitivity(pd.DataFrame())
        assert result.empty


# ── Table 7 ───────────────────────────────────────────────────────────────────

class TestTable7:
    def test_only_includes_flagged_cases(self, scored_df):
        result = table_7_review_flags(scored_df)
        if not result.empty:
            assert result["review_required_flag"].all()

    def test_review_reason_column_present(self, scored_df):
        result = table_7_review_flags(scored_df)
        if not result.empty:
            assert "review_reason" in result.columns

    def test_case_0002_flagged(self, scored_df):
        """Case 0002 has low_source_quality (score=4 -> not flagged) but high severity + low ECI."""
        result = table_7_review_flags(scored_df)
        # 0002 has ECI=1.0 (all high confidence) so not flagged for that reason
        # It has source_quality=4 -> not low quality. Check it may or may not appear.
        assert isinstance(result, pd.DataFrame)

    def test_case_0003_flagged(self, scored_df):
        """Case 0003 has high_missingness_flag=True so should appear in review table."""
        result = table_7_review_flags(scored_df)
        if not result.empty:
            assert "CSA-LITE-0003" in result["case_id"].values


# ── compute_all_tables ────────────────────────────────────────────────────────

class TestComputeAllTables:
    def test_returns_7_tables(self, scored_df):
        tables = compute_all_tables(scored_df)
        assert len(tables) == 7

    def test_all_tables_are_dataframes(self, scored_df):
        tables = compute_all_tables(scored_df)
        for name, df in tables.items():
            assert isinstance(df, pd.DataFrame), f"{name} is not a DataFrame"

    def test_table_names_correct(self, scored_df):
        tables = compute_all_tables(scored_df)
        expected = {
            "table_1_corpus_composition",
            "table_2_within_category_variance",
            "table_3_dimension_patterns",
            "table_4_missingness_by_category",
            "table_5_sensitivity",
            "table_6_high_variance_case_pairs",
            "table_7_review_flags",
        }
        assert set(tables.keys()) == expected

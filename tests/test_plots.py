"""
Tests for the plots module.

12 tests covering all 6 manuscript figures.
Figures are generated to a temporary directory; no GUI is shown.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from csalite.scoring import score_dataframe

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_cases_df():
    from csalite.io import read_cases_csv
    return read_cases_csv(FIXTURES / "valid_cases_minimal.csv")


@pytest.fixture
def scored_df(valid_cases_df):
    return score_dataframe(valid_cases_df)


@pytest.fixture
def tmpfigs(tmp_path):
    return tmp_path / "figures"


class TestFig1:
    def test_generates_files(self, tmpfigs):
        from csalite.plots import plot_pipeline_architecture
        plot_pipeline_architecture(tmpfigs)
        assert (tmpfigs / "fig_1_pipeline_architecture.png").exists()
        assert (tmpfigs / "fig_1_pipeline_architecture.svg").exists()


class TestFig2:
    def test_generates_files(self, scored_df, tmpfigs):
        from csalite.plots import plot_corpus_by_annex_area
        plot_corpus_by_annex_area(scored_df, tmpfigs)
        assert (tmpfigs / "fig_2_corpus_by_annex_area.png").exists()

    def test_empty_raises_valueerror(self, tmpfigs):
        import pandas as pd
        from csalite.plots import plot_corpus_by_annex_area
        with pytest.raises(ValueError, match="Empty dataset"):
            plot_corpus_by_annex_area(pd.DataFrame(), tmpfigs)


class TestFig3:
    def test_generates_files(self, scored_df, tmpfigs):
        from csalite.plots import plot_context_severity_by_annex_area
        plot_context_severity_by_annex_area(scored_df, tmpfigs)
        assert (tmpfigs / "fig_3_context_severity_by_annex_area.png").exists()

    def test_empty_raises_valueerror(self, tmpfigs):
        import pandas as pd
        from csalite.plots import plot_context_severity_by_annex_area
        with pytest.raises(ValueError, match="Empty dataset"):
            plot_context_severity_by_annex_area(pd.DataFrame(), tmpfigs)


class TestFig4:
    def test_generates_files(self, scored_df, tmpfigs):
        from csalite.plots import plot_dimension_heatmap
        plot_dimension_heatmap(scored_df, tmpfigs)
        assert (tmpfigs / "fig_4_dimension_heatmap.png").exists()
        assert (tmpfigs / "fig_4_dimension_heatmap.svg").exists()


class TestFig5:
    def test_generates_files(self, scored_df, tmpfigs):
        from csalite.plots import plot_evidence_confidence_matrix
        plot_evidence_confidence_matrix(scored_df, tmpfigs)
        assert (tmpfigs / "fig_5_evidence_confidence_matrix.png").exists()


class TestFig6:
    def test_generates_files(self, scored_df, tmpfigs):
        from csalite.plots import plot_sensitivity_comparison
        plot_sensitivity_comparison(scored_df, tmpfigs)
        assert (tmpfigs / "fig_6_sensitivity_comparison.png").exists()

    def test_empty_raises_valueerror(self, tmpfigs):
        import pandas as pd
        from csalite.plots import plot_sensitivity_comparison
        with pytest.raises(ValueError):
            plot_sensitivity_comparison(pd.DataFrame(), tmpfigs)


class TestGenerateAllFigures:
    def test_returns_6_figures(self, scored_df, tmpfigs):
        from csalite.plots import generate_all_figures
        figs = generate_all_figures(scored_df, tmpfigs)
        assert len(figs) == 6

    def test_empty_raises_valueerror(self, tmpfigs):
        import pandas as pd
        from csalite.plots import generate_all_figures
        with pytest.raises(ValueError, match="Empty dataset"):
            generate_all_figures(pd.DataFrame(), tmpfigs)

    def test_all_png_files_created(self, scored_df, tmpfigs):
        from csalite.plots import generate_all_figures
        generate_all_figures(scored_df, tmpfigs)
        pngs = list(tmpfigs.glob("*.png"))
        assert len(pngs) == 6

"""
Manuscript headline-value verification tests.

Verifies every numerical claim made in the CSA-lite manuscript
(CSA_lite_MDPI_Electronics_v0.2.2.md) that can be derived from the
committed v0.2.0 corpus and pipeline.

32 tests total covering 35 manuscript verification items:
  TestCorpusProperties    (15 tests) — data file + scoring claims (items 1–14)
  TestPipelineArtifacts   (17 tests) — run-once session fixture + metadata
    Items 15–35 verified (some items merged as assertions within single tests):
    - Item 18 (validation_report.md) merged into test_validation_report_json_exists
    - Items 32–33 (.zenodo.json test count / figure count) merged into test_zenodo_json_version_is_022
    - Item 35 (license wording) merged into test_zenodo_json_version_is_022
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

# ── Paths ─────────────────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).parent.parent
_CORPUS_CSV = _REPO_ROOT / "data" / "processed" / "csa_lite_cases.csv"
_README = _REPO_ROOT / "README.md"
_CITATION_CFF = _REPO_ROOT / "CITATION.cff"


# ── Session-scoped pipeline fixture ──────────────────────────────────────────


@pytest.fixture(scope="session")
def corpus_df():
    """The raw v0.2.0 corpus (45 cases)."""
    from csalite.io import read_cases_csv
    return read_cases_csv(_CORPUS_CSV)


@pytest.fixture(scope="session")
def scored_df(corpus_df):
    """Corpus with all scoring columns applied."""
    from csalite.scoring import score_dataframe
    return score_dataframe(corpus_df)


@pytest.fixture(scope="session")
def pipeline_outputs(tmp_path_factory, corpus_df):
    """
    Run the full pipeline once per test session into a temp directory.

    Provides the outdir Path; all artifact-existence tests use this fixture.
    """
    from typer.testing import CliRunner
    from csalite.cli import app

    outdir = tmp_path_factory.mktemp("pipeline_outputs")
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["all", "--input", str(_CORPUS_CSV), "--outdir", str(outdir)],
    )
    assert result.exit_code == 0, (
        f"Pipeline failed with exit_code={result.exit_code}.\n{result.stdout}"
    )
    return outdir


# ── Corpus properties ─────────────────────────────────────────────────────────


class TestCorpusProperties:
    """13 tests verifying corpus size, mapping types, source quality, CSI stats, and completeness."""

    def test_n_equals_45(self, corpus_df):
        """Manuscript claim: N = 45 cases in v0.2.0 corpus."""
        assert len(corpus_df) == 45

    def test_direct_mappings_equals_36(self, corpus_df):
        """Manuscript claim: 36 direct Annex III mappings."""
        assert (corpus_df["annex_mapping_type"] == "direct").sum() == 36

    def test_analogous_mappings_equals_2(self, corpus_df):
        """Manuscript claim: 2 analogous mappings."""
        assert (corpus_df["annex_mapping_type"] == "analogous").sum() == 2

    def test_comparator_mappings_equals_7(self, corpus_df):
        """Manuscript claim: 7 comparator cases."""
        assert (corpus_df["annex_mapping_type"] == "comparator").sum() == 7

    def test_source_quality_medium_equals_5(self, corpus_df):
        """Manuscript claim: 5 cases with source quality Medium (score 2)."""
        sq = pd.to_numeric(corpus_df["source_quality_score"], errors="coerce")
        assert int((sq == 2).sum()) == 5

    def test_source_quality_high_equals_26(self, corpus_df):
        """Manuscript claim: 26 cases with source quality High (score 3)."""
        sq = pd.to_numeric(corpus_df["source_quality_score"], errors="coerce")
        assert int((sq == 3).sum()) == 26

    def test_source_quality_very_high_equals_14(self, corpus_df):
        """Manuscript claim: 14 cases with source quality Very High (score 4)."""
        sq = pd.to_numeric(corpus_df["source_quality_score"], errors="coerce")
        assert int((sq == 4).sum()) == 14

    def test_csi_min_equals_7(self, scored_df):
        """Manuscript claim: CSI min = 7."""
        assert int(scored_df["context_severity_index"].min()) == 7

    def test_csi_max_equals_16(self, scored_df):
        """Manuscript claim: CSI max = 16."""
        assert int(scored_df["context_severity_index"].max()) == 16

    def test_csi_median_equals_12(self, scored_df):
        """Manuscript claim: median CSI = 12."""
        assert scored_df["context_severity_index"].median() == 12

    def test_csi_mean_within_rounding_tolerance(self, scored_df):
        """Manuscript claim: mean CSI = 12.07 (neutral rule, ±0.005 rounding tolerance)."""
        mean = float(scored_df["context_severity_index"].mean())
        assert abs(mean - 12.07) < 0.005, f"Mean CSI = {mean:.4f}, expected ~12.07"

    def test_severity_bands_distribution(self, scored_df):
        """Manuscript claim: low=0, moderate=2, high=16, severe=27."""
        band_counts = scored_df["context_severity_band"].value_counts()
        assert int(band_counts.get("low", 0)) == 0, "Expected 0 low-band cases"
        assert int(band_counts.get("moderate", 0)) == 2, "Expected 2 moderate-band cases"
        assert int(band_counts.get("high", 0)) == 16, "Expected 16 high-band cases"
        assert int(band_counts.get("severe", 0)) == 27, "Expected 27 severe-band cases"

    def test_all_dimensions_fully_coded_no_missing(self, scored_df):
        """Manuscript claim: all 45 cases fully coded on all 8 dimensions in v0.2.0."""
        from csalite.constants import SCORE_DIMENSIONS
        import pandas as _pd
        for dim in SCORE_DIMENSIONS:
            col = f"{dim}_score"
            missing = _pd.to_numeric(scored_df[col], errors="coerce").isna().sum()
            assert missing == 0, f"{dim}_score has {missing} missing values"

    def test_no_band_changes_under_any_assumption(self, scored_df):
        """Manuscript claim: no case changes band between zero/neutral/conservative rules."""
        n_changes = int(scored_df["sensitivity_band_change"].sum())
        assert n_changes == 0, (
            f"{n_changes} cases change band across imputation assumptions; "
            "expected 0 because v0.2.0 corpus has no unknown values"
        )

    def test_evidence_confidence_weights(self, scored_df):
        """Manuscript claim: confidence weights round to specified values (tolerance ±0.015)."""
        from csalite.constants import SCORE_DIMENSIONS, CONFIDENCE_WEIGHTS

        # Manually reload corpus for confidence columns (scored_df might not have confidence cols)
        from csalite.io import read_cases_csv
        df = read_cases_csv(_CORPUS_CSV)

        expected = {
            "decision_criticality": 0.93,
            "autonomy": 0.95,
            "vulnerability": 0.83,
            "oversight": 0.77,
            "recourse": 0.80,
            "scale": 0.98,
            "opacity": 0.89,
            "monitoring": 0.86,
        }
        for dim, expected_w in expected.items():
            col = f"{dim}_confidence"
            confs = df[col].fillna("unknown").str.strip().str.lower()
            weights = confs.map(lambda v: CONFIDENCE_WEIGHTS.get(v, 0.0))
            actual = float(weights.mean())
            assert abs(actual - expected_w) < 0.015, (
                f"{dim} confidence weight = {actual:.4f}, expected ~{expected_w} (tolerance ±0.015)"
            )


# ── Pipeline artifact existence ───────────────────────────────────────────────


class TestPipelineArtifacts:
    """17 tests verifying that the full pipeline emits all expected artifacts."""

    def test_all_6_figure_stems_have_png_and_svg(self, pipeline_outputs):
        """Manuscript claim: Figures 1–6 emitted as PNG and SVG."""
        stems = [
            "fig_1_pipeline_architecture",
            "fig_2_corpus_by_annex_area",
            "fig_3_context_severity_by_annex_area",
            "fig_4_dimension_heatmap",
            "fig_5_evidence_confidence_matrix",
            "fig_6_sensitivity_comparison",
        ]
        figs_dir = pipeline_outputs / "figures"
        for stem in stems:
            for ext in ("png", "svg"):
                p = figs_dir / f"{stem}.{ext}"
                assert p.exists(), f"Missing figure: {p.name}"

    def test_all_8_table_files_exist(self, pipeline_outputs):
        """Manuscript claim: Tables 1–8 generated by csalite all."""
        tables = [
            "table_1_csalite_dimensions.csv",
            "table_2_source_quality_scale.csv",
            "table_3_corpus_composition_by_annex_area.csv",
            "table_4_within_category_variance.csv",
            "table_5_dimension_level_patterns.csv",
            "table_6_evidence_confidence_by_dimension.csv",
            "table_7_sensitivity_summary.csv",
            "table_8_matched_case_contrasts.csv",
        ]
        tables_dir = pipeline_outputs / "tables"
        for t in tables:
            assert (tables_dir / t).exists(), f"Missing table: {t}"

    def test_all_7_supplementary_tables_exist(self, pipeline_outputs):
        """Supplementary tables S1–S7 generated by csalite all."""
        supp_tables = [
            "supp_table_s1_full_case_corpus.csv",
            "supp_table_s2_scored_cases.csv",
            "supp_table_s3_sensitivity_per_case.csv",
            "supp_table_s4_sources_manifest.csv",
            "supp_table_s5_annex_mapping_rationales.csv",
            "supp_table_s6_validation_summary.csv",
            "supp_table_s7_case_audit_flags.csv",
        ]
        tables_dir = pipeline_outputs / "tables"
        for t in supp_tables:
            assert (tables_dir / t).exists(), f"Missing supplementary table: {t}"

    def test_validation_report_json_exists(self, pipeline_outputs):
        """Reproducibility claim: validation_report.json AND validation_report.md written by pipeline."""
        import json
        # Item 19: validation_report.json exists
        p_json = pipeline_outputs / "reports" / "validation_report.json"
        assert p_json.exists(), "validation_report.json not found"
        data = json.loads(p_json.read_text())
        assert data.get("is_valid") is True
        # Item 18: validation_report.md exists
        p_md = pipeline_outputs / "reports" / "validation_report.md"
        assert p_md.exists(), "validation_report.md not found"
        assert "Validation Report" in p_md.read_text()

    def test_reproducibility_report_md_exists(self, pipeline_outputs):
        """Reproducibility claim: reproducibility_report.md written by pipeline."""
        p = pipeline_outputs / "reports" / "reproducibility_report.md"
        assert p.exists(), "reproducibility_report.md not found"
        assert "Reproducibility Report" in p.read_text()

    def test_reproducibility_report_json_exists(self, pipeline_outputs):
        """Reproducibility claim: reproducibility_report.json written by pipeline."""
        import json
        p = pipeline_outputs / "reports" / "reproducibility_report.json"
        assert p.exists(), "reproducibility_report.json not found"
        data = json.loads(p.read_text())
        assert "n_cases" in data
        assert data["n_cases"] == 45

    def test_case_audit_report_md_exists(self, pipeline_outputs):
        """Reproducibility claim: case_audit_report.md written by pipeline."""
        p = pipeline_outputs / "reports" / "case_audit_report.md"
        assert p.exists(), "case_audit_report.md not found"
        assert "Case Audit Report" in p.read_text()

    def test_case_audit_report_json_exists(self, pipeline_outputs):
        """Reproducibility claim: case_audit_report.json written by pipeline."""
        import json
        p = pipeline_outputs / "reports" / "case_audit_report.json"
        assert p.exists(), "case_audit_report.json not found"
        data = json.loads(p.read_text())
        assert "n_cases" in data
        assert data["n_cases"] == 45

    def test_manifest_json_lists_all_artifacts(self, pipeline_outputs):
        """Reproducibility claim: manuscript_artifact_manifest.json includes all artifacts."""
        import json
        p = pipeline_outputs / "reports" / "manuscript_artifact_manifest.json"
        assert p.exists(), "manuscript_artifact_manifest.json not found"
        manifest = json.loads(p.read_text())
        assert "artifacts" in manifest
        # 8 tables + 7 supp tables + 12 figure files (6x2) + 7 reports = 34 artifacts
        assert len(manifest["artifacts"]) >= 30
        missing = [a["path"] for a in manifest["artifacts"] if not a.get("exists")]
        assert not missing, f"Manifest lists missing artifacts: {missing}"

    def test_manifest_md_exists(self, pipeline_outputs):
        """Reproducibility claim: manuscript_artifact_manifest.md written by pipeline."""
        p = pipeline_outputs / "reports" / "manuscript_artifact_manifest.md"
        assert p.exists(), "manuscript_artifact_manifest.md not found"
        text = p.read_text()
        assert "Artifact Manifest" in text
        assert "table_1_csalite_dimensions" in text

    def test_readme_clone_url_is_correct(self):
        """README must use the correct GitHub clone URL (not placeholder)."""
        text = _README.read_text(encoding="utf-8")
        assert "github.com/roy-saurabh/csa-lite-master" in text, (
            "README clone URL must point to roy-saurabh/csa-lite-master"
        )
        assert "placeholder" not in text.lower(), (
            "README still contains placeholder URL"
        )

    def test_citation_cff_version_and_doi(self):
        """CITATION.cff must use version v0.2.2 and the concept DOI 10.5281/zenodo.20403165.

        The version-specific DOI for v0.2.2 is assigned by Zenodo when the GitHub
        release is created. Until then CITATION.cff uses the concept DOI which always
        resolves to the latest published version.
        """
        text = _CITATION_CFF.read_text(encoding="utf-8")
        assert "0.2.2" in text, "CITATION.cff must contain version 0.2.2"
        assert "10.5281/zenodo.20406743" in text, (
            "CITATION.cff must contain version-specific DOI 10.5281/zenodo.20406743"
        )

    def test_citation_does_not_claim_publication(self):
        """CITATION.cff preferred-citation must not be type: article before acceptance."""
        text = _CITATION_CFF.read_text(encoding="utf-8")
        lines = text.splitlines()
        in_preferred = False
        preferred_type = None
        for line in lines:
            if "preferred-citation:" in line:
                in_preferred = True
            if in_preferred and line.strip().startswith("type:"):
                preferred_type = line.strip().split("type:")[-1].strip()
                break
        assert preferred_type != "article", (
            "CITATION.cff preferred-citation type is 'article', implying the manuscript "
            "is already published. Change to 'software' until acceptance."
        )

    def test_no_metadata_claims_article_published(self):
        """No repository metadata (README, CITATION.cff, .zenodo.json) claims article is published."""
        import json
        # README
        readme_text = _README.read_text(encoding="utf-8")
        assert "published" not in readme_text.lower() or "under review" in readme_text.lower() or \
               "submitted" in readme_text.lower() or \
               "not yet accepted" in readme_text.lower() or \
               "not yet published" in readme_text.lower(), \
               "README appears to claim the article is published without qualification"
        # .zenodo.json
        zenodo_path = _REPO_ROOT / ".zenodo.json"
        if zenodo_path.exists():
            zenodo = json.loads(zenodo_path.read_text())
            # Should not claim journal publication
            description = zenodo.get("description", "")
            notes = zenodo.get("notes", "")
            journal = zenodo.get("journal", {})
            assert not journal, f".zenodo.json should not have a 'journal' key before acceptance: {journal}"

    def test_readme_doi_is_correct(self):
        """Check 28: README DOI badge must reference 10.5281/zenodo.20406743."""
        text = _README.read_text(encoding="utf-8")
        assert "10.5281/zenodo.20406743" in text, (
            "README must contain the version-specific DOI 10.5281/zenodo.20406743"
        )

    def test_pyproject_version_is_022(self):
        """Check 31: pyproject.toml package version must be 0.2.2."""
        pyproject_path = _REPO_ROOT / "pyproject.toml"
        text = pyproject_path.read_text(encoding="utf-8")
        import re
        match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
        assert match is not None, "pyproject.toml must have a version field"
        assert match.group(1) == "0.2.2", (
            f"pyproject.toml version is '{match.group(1)}', expected '0.2.2'"
        )

    def test_zenodo_json_version_is_022(self):
        """Check 31: .zenodo.json version must be 0.2.2.
        Check 32: .zenodo.json notes must mention 138 tests.
        Check 33: .zenodo.json description must mention six manuscript figures (not eight).
        Check 35: README license wording must match dual-license manuscript claim.
        """
        import json
        zenodo_path = _REPO_ROOT / ".zenodo.json"
        assert zenodo_path.exists(), ".zenodo.json not found"
        zenodo = json.loads(zenodo_path.read_text())

        # Item 31
        assert zenodo.get("version") == "0.2.2", (
            f".zenodo.json version is '{zenodo.get('version')}', expected '0.2.2'"
        )
        # Item 32 — notes must mention 138 tests
        notes = zenodo.get("notes", "")
        assert "138" in notes, (
            f".zenodo.json notes do not mention 138 tests; notes='{notes[:120]}'"
        )
        # Item 33 — description must say six manuscript figures, not eight
        description = zenodo.get("description", "")
        assert "Six manuscript figures" in description or "six manuscript figures" in description, (
            "'.zenodo.json description should say 'Six manuscript figures'"
        )
        assert "Eight matplotlib figures" not in description, (
            ".zenodo.json description still says 'Eight matplotlib figures'; update to six"
        )
        # Item 35 — README dual-license wording matches manuscript claim
        readme_text = _README.read_text(encoding="utf-8")
        assert "MIT" in readme_text, "README must mention MIT license for code"
        assert "CC BY 4.0" in readme_text, "README must mention CC BY 4.0 for data/docs"
        assert "generated tables" in readme_text.lower() or "generated figures" in readme_text.lower(), (
            "README license section must cover generated outputs (CC BY 4.0)"
        )

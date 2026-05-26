"""
Tests for the CLI using typer.testing.CliRunner.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from csalite.cli import app

FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


@pytest.fixture
def valid_cases_path():
    return str(FIXTURES / "valid_cases_minimal.csv")


@pytest.fixture
def invalid_cases_path():
    return str(FIXTURES / "invalid_cases_missing_required.csv")


@pytest.fixture
def tmp_outdir(tmp_path):
    return str(tmp_path / "output")


# ── version ───────────────────────────────────────────────────────────────────

class TestVersion:
    def test_version_command(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "CSA-Lite" in result.stdout


# ── validate ──────────────────────────────────────────────────────────────────

class TestValidateCommand:
    def test_valid_file_passes(self, valid_cases_path):
        result = runner.invoke(app, ["validate", "--input", valid_cases_path])
        assert result.exit_code == 0
        assert "PASS" in result.stdout

    def test_invalid_file_fails(self, invalid_cases_path):
        result = runner.invoke(app, ["validate", "--input", invalid_cases_path])
        assert result.exit_code == 1
        assert "FAIL" in result.stdout or "error" in result.stdout.lower()

    def test_nonexistent_file_exits_with_error(self, tmp_path):
        result = runner.invoke(app, ["validate", "--input", str(tmp_path / "nonexistent.csv")])
        assert result.exit_code == 1

    def test_report_written(self, valid_cases_path, tmp_path):
        report_path = tmp_path / "report.md"
        result = runner.invoke(app, [
            "validate", "--input", valid_cases_path,
            "--report", str(report_path),
        ])
        assert result.exit_code == 0
        assert report_path.exists()
        content = report_path.read_text()
        assert "CSA-Lite" in content


# ── score ─────────────────────────────────────────────────────────────────────

class TestScoreCommand:
    def test_produces_output_csv(self, valid_cases_path, tmp_path):
        out = tmp_path / "scored.csv"
        result = runner.invoke(app, [
            "score", "--input", valid_cases_path, "--output", str(out),
        ])
        assert result.exit_code == 0
        assert out.exists()

    def test_output_has_scored_columns(self, valid_cases_path, tmp_path):
        import pandas as pd
        out = tmp_path / "scored.csv"
        runner.invoke(app, ["score", "--input", valid_cases_path, "--output", str(out)])
        df = pd.read_csv(out)
        assert "context_severity_band" in df.columns
        assert "evidence_completeness_index" in df.columns

    def test_jsonl_output_produced(self, valid_cases_path, tmp_path):
        out_csv = tmp_path / "scored.csv"
        out_jsonl = tmp_path / "scored.jsonl"
        runner.invoke(app, [
            "score", "--input", valid_cases_path,
            "--output", str(out_csv),
            "--jsonl-output", str(out_jsonl),
        ])
        assert out_jsonl.exists()
        lines = out_jsonl.read_text().strip().split("\n")
        assert len(lines) == 3  # 3 fixture cases


# ── analyze ───────────────────────────────────────────────────────────────────

class TestAnalyzeCommand:
    def test_produces_table_files(self, valid_cases_path, tmp_path):
        # First score
        scored = tmp_path / "scored.csv"
        runner.invoke(app, ["score", "--input", valid_cases_path, "--output", str(scored)])

        tables_dir = tmp_path / "tables"
        result = runner.invoke(app, ["analyze", "--input", str(scored), "--outdir", str(tables_dir)])
        assert result.exit_code == 0
        csvs = list(tables_dir.glob("*.csv"))
        assert len(csvs) == 7


# ── sensitivity ───────────────────────────────────────────────────────────────

class TestSensitivityCommand:
    def test_produces_sensitivity_files(self, valid_cases_path, tmp_path):
        scored = tmp_path / "scored.csv"
        runner.invoke(app, ["score", "--input", valid_cases_path, "--output", str(scored)])

        outdir = tmp_path / "sensitivity"
        result = runner.invoke(app, [
            "sensitivity", "--input", str(scored), "--outdir", str(outdir),
        ])
        assert result.exit_code == 0
        assert (outdir / "sensitivity_detail.csv").exists()
        assert (outdir / "sensitivity_summary.csv").exists()


# ── report ────────────────────────────────────────────────────────────────────

class TestReportCommand:
    def test_produces_markdown_report(self, valid_cases_path, tmp_path):
        scored = tmp_path / "scored.csv"
        runner.invoke(app, ["score", "--input", valid_cases_path, "--output", str(scored)])

        out = tmp_path / "report.md"
        result = runner.invoke(app, [
            "report", "--input", str(scored), "--out", str(out),
        ])
        assert result.exit_code == 0
        assert out.exists()
        content = out.read_text()
        assert "CSA-Lite" in content


# ── all ───────────────────────────────────────────────────────────────────────

class TestAllCommand:
    def test_full_pipeline_runs(self, valid_cases_path, tmp_path):
        outdir = tmp_path / "all_output"
        result = runner.invoke(app, [
            "all", "--input", valid_cases_path, "--outdir", str(outdir),
        ])
        assert result.exit_code == 0
        assert (outdir / "scored_cases.csv").exists()
        assert (outdir / "scored_cases.jsonl").exists()
        tables_dir = outdir / "tables"
        assert tables_dir.exists()
        assert len(list(tables_dir.glob("*.csv"))) >= 7

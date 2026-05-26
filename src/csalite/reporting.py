"""
Report generation for CSA-lite.

Produces a structured Markdown validation and scoring report.
No I/O except the final write — callers supply paths.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from csalite.constants import DISCLAIMER, PROJECT_NAME, PROJECT_VERSION
from csalite.validation import ValidationResult


def _pct(n: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{100 * n / total:.1f}%"


def build_validation_report(
    result: ValidationResult,
    input_path: Optional[Path] = None,
    n_cases: int = 0,
) -> str:
    """
    Build a Markdown validation report from a ValidationResult.

    Parameters
    ----------
    result: ValidationResult from validation.validate_dataframe
    input_path: source file path (for display)
    n_cases: number of cases in the input

    Returns
    -------
    Markdown string.
    """
    lines: list[str] = []

    lines.append(f"# {PROJECT_NAME} v{PROJECT_VERSION} — Validation Report")
    lines.append(f"\n_Generated: {datetime.datetime.now().isoformat(timespec='seconds')}_\n")

    if input_path:
        lines.append(f"**Input file:** `{input_path}`  ")
    lines.append(f"**Cases checked:** {n_cases}  ")
    lines.append(f"**Status:** {'PASS' if result.is_valid else 'FAIL'}  ")
    lines.append(f"**Errors:** {len(result.errors)}  ")
    lines.append(f"**Warnings:** {len(result.warnings)}  ")

    lines.append("\n---\n")
    lines.append("> **Disclaimer:** " + DISCLAIMER)
    lines.append("\n---\n")

    if result.errors:
        lines.append("## Errors\n")
        for issue in result.errors:
            lines.append(
                f"- `[{issue.rule_id}]` **{issue.field}** (case: `{issue.case_id}`): "
                f"{issue.message}"
            )
        lines.append("")

    if result.warnings:
        lines.append("## Warnings\n")
        for issue in result.warnings:
            lines.append(
                f"- `[{issue.rule_id}]` {issue.field} (case: `{issue.case_id}`): "
                f"{issue.message}"
            )
        lines.append("")

    info_issues = [i for i in result.issues if i.severity.value == "info"]
    if info_issues:
        lines.append("## Informational\n")
        for issue in info_issues:
            lines.append(
                f"- `[{issue.rule_id}]` {issue.field} (case: `{issue.case_id}`): "
                f"{issue.message}"
            )
        lines.append("")

    lines.append("## Rule Summary\n")
    rule_counts: dict[str, int] = {}
    for issue in result.issues:
        rule_counts[issue.rule_id] = rule_counts.get(issue.rule_id, 0) + 1
    if rule_counts:
        lines.append("| Rule | Count |")
        lines.append("|------|-------|")
        for rule, count in sorted(rule_counts.items()):
            lines.append(f"| {rule} | {count} |")
    else:
        lines.append("No issues found.")

    return "\n".join(lines) + "\n"


def build_scoring_summary_report(
    scored_df: pd.DataFrame,
    validation_result: Optional[ValidationResult] = None,
) -> str:
    """
    Build a Markdown summary report for a scored dataset.
    """
    lines: list[str] = []

    lines.append(f"# {PROJECT_NAME} v{PROJECT_VERSION} — Scoring Summary Report")
    lines.append(f"\n_Generated: {datetime.datetime.now().isoformat(timespec='seconds')}_\n")
    lines.append("> **Disclaimer:** " + DISCLAIMER)
    lines.append("\n---\n")

    n = len(scored_df)
    lines.append(f"## Dataset Overview\n")
    lines.append(f"- **Total cases:** {n}")

    if "annex_iii_area" in scored_df.columns:
        area_counts = scored_df["annex_iii_area"].value_counts().sort_index()
        lines.append(f"- **Annex III areas represented:** {len(area_counts)}")

    if "context_severity_band" in scored_df.columns and n > 0:
        band_counts = scored_df["context_severity_band"].value_counts()
        lines.append("\n## Severity Band Distribution (CSI, neutral imputation)\n")
        lines.append("| Band | Count | % |")
        lines.append("|------|-------|---|")
        for band in ["low", "moderate", "high", "severe", "unknown"]:
            cnt = int(band_counts.get(band, 0))
            lines.append(f"| {band} | {cnt} | {_pct(cnt, n)} |")

    if "evidence_completeness_index" in scored_df.columns and n > 0:
        eci = pd.to_numeric(scored_df["evidence_completeness_index"], errors="coerce")
        lines.append(f"\n## Evidence Completeness\n")
        lines.append(f"- **Mean ECI:** {eci.mean():.3f}")
        lines.append(f"- **Median ECI:** {eci.median():.3f}")
        lines.append(f"- **Min ECI:** {eci.min():.3f}")
        lines.append(f"- **Max ECI:** {eci.max():.3f}")

    if n > 0:
        flag_cols = [
            "high_missingness_flag",
            "low_source_quality_flag",
            "sensitivity_band_change",
            "review_required_flag",
        ]
        flag_cols = [c for c in flag_cols if c in scored_df.columns]
        if flag_cols:
            lines.append("\n## Review Flags\n")
            lines.append("| Flag | Count | % |")
            lines.append("|------|-------|---|")
            for col in flag_cols:
                # Handle bool, np.bool_, or string representation of booleans
                series = scored_df[col]
                if series.dtype == object:
                    bool_series = series.map(
                        lambda v: str(v).strip().lower() in ("true", "1", "yes")
                    )
                else:
                    bool_series = series.astype(bool)
                cnt = int(bool_series.sum())
                lines.append(f"| {col} | {cnt} | {_pct(cnt, n)} |")

    if validation_result is not None:
        lines.append("\n## Validation Status\n")
        lines.append(f"- **Status:** {'PASS' if validation_result.is_valid else 'FAIL'}")
        lines.append(f"- **Errors:** {len(validation_result.errors)}")
        lines.append(f"- **Warnings:** {len(validation_result.warnings)}")

    return "\n".join(lines) + "\n"


def write_report(content: str, path: Path) -> None:
    """Write a Markdown report string to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

"""
Report generation for CSA-lite.

Produces structured Markdown and JSON reports for validation, scoring,
reproducibility, case audit, and the artifact manifest.
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


def build_validation_report_json(
    result: ValidationResult,
    n_cases: int = 0,
    input_path: Optional[Path] = None,
) -> dict:
    """
    Build a structured JSON-serialisable dict of the validation result.

    Suitable for writing as outputs/reports/validation_report.json.
    """
    return {
        "schema": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "input_file": str(input_path) if input_path else None,
        "n_cases": n_cases,
        "is_valid": result.is_valid,
        "n_errors": len(result.errors),
        "n_warnings": len(result.warnings),
        "errors": [
            {
                "rule_id": e.rule_id,
                "field": e.field,
                "case_id": e.case_id,
                "message": e.message,
            }
            for e in result.errors
        ],
        "warnings": [
            {
                "rule_id": w.rule_id,
                "field": w.field,
                "case_id": w.case_id,
                "message": w.message,
            }
            for w in result.warnings
        ],
    }


def build_reproducibility_report_json(
    n_cases: int,
    input_path: Optional[Path],
    outdir: Path,
    run_timestamp: Optional[str] = None,
    validation_result: Optional[ValidationResult] = None,
) -> dict:
    """
    Build a JSON-serialisable reproducibility report dict.

    Suitable for outputs/reports/reproducibility_report.json.
    """
    import sys
    import importlib

    ts = run_timestamp or datetime.datetime.now().isoformat(timespec="seconds")

    pkg_versions: dict[str, str] = {}
    for pkg in ["pandas", "numpy", "matplotlib", "pydantic", "pandera", "typer", "rich"]:
        try:
            mod = importlib.import_module(pkg)
            pkg_versions[pkg] = getattr(mod, "__version__", "unknown")
        except ImportError:
            pkg_versions[pkg] = "not installed"

    table_names = [
        "table_1_csalite_dimensions.csv",
        "table_2_corpus_composition_by_annex_area.csv",
        "table_3_within_category_variance.csv",
        "table_4_dimension_level_patterns.csv",
        "table_5_evidence_confidence_by_dimension.csv",
        "table_6_sensitivity_summary.csv",
        "table_7_matched_case_contrasts.csv",
    ]
    supp_table_names = [
        "supp_table_s1_full_case_corpus.csv",
        "supp_table_s2_scored_cases.csv",
        "supp_table_s3_sensitivity_per_case.csv",
        "supp_table_s4_sources_manifest.csv",
        "supp_table_s5_annex_mapping_rationales.csv",
        "supp_table_s6_validation_summary.csv",
        "supp_table_s7_case_audit_flags.csv",
    ]
    fig_stems = [
        "fig_1_pipeline_architecture",
        "fig_2_corpus_by_annex_area",
        "fig_3_context_severity_by_annex_area",
        "fig_4_dimension_heatmap",
        "fig_5_evidence_confidence_matrix",
        "fig_6_sensitivity_comparison",
    ]

    tables_status = {t: (outdir / "tables" / t).exists() for t in table_names}
    supp_tables_status = {t: (outdir / "tables" / t).exists() for t in supp_table_names}
    figs_status: dict[str, bool] = {}
    for stem in fig_stems:
        for ext in ("png", "svg"):
            fname = f"{stem}.{ext}"
            figs_status[fname] = (outdir / "figures" / fname).exists()

    val_summary = None
    if validation_result is not None:
        val_summary = {
            "is_valid": validation_result.is_valid,
            "n_errors": len(validation_result.errors),
            "n_warnings": len(validation_result.warnings),
        }

    return {
        "schema": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "generated": ts,
        "input_file": str(input_path) if input_path else None,
        "n_cases": n_cases,
        "command": f"csalite all --input {input_path} --outdir {outdir}",
        "python_version": sys.version,
        "package_versions": pkg_versions,
        "validation": val_summary,
        "tables": tables_status,
        "supplementary_tables": supp_tables_status,
        "figures": figs_status,
        "outdir": str(outdir),
    }


def build_case_audit_report(
    df: pd.DataFrame,
    run_timestamp: Optional[str] = None,
) -> tuple[str, dict]:
    """
    Build a case audit report in both Markdown and JSON formats.

    Parameters
    ----------
    df : scored DataFrame (must include context_severity_index).
    run_timestamp : ISO timestamp string.

    Returns
    -------
    (markdown_str, json_dict)
    """
    from csalite.analysis import supp_table_s7_case_audit_flags
    from csalite.validation import validate_dataframe

    ts = run_timestamp or datetime.datetime.now().isoformat(timespec="seconds")
    audit_df = supp_table_s7_case_audit_flags(df)
    val_result = validate_dataframe(df)

    n_cases = len(df)
    n_blocking = int((audit_df["audit_severity"] == "blocking").sum())
    n_major = int((audit_df["audit_severity"] == "major").sum())
    n_minor = int((audit_df["audit_severity"] == "minor").sum())
    n_info = int((audit_df["audit_severity"] == "informational").sum())

    # ── Markdown ──────────────────────────────────────────────────────────────
    lines: list[str] = []
    lines.append(f"# {PROJECT_NAME} v{PROJECT_VERSION} — Case Audit Report")
    lines.append(f"\n_Generated: {ts}_\n")
    lines.append("> **Disclaimer:** " + DISCLAIMER)
    lines.append("\n---\n")

    lines.append("## Audit Summary\n")
    lines.append(f"- **Cases audited:** {n_cases}")
    lines.append(f"- **Validation status:** {'PASS' if val_result.is_valid else 'FAIL'}")
    lines.append(f"- **Validation errors:** {len(val_result.errors)}")
    lines.append(f"- **Validation warnings:** {len(val_result.warnings)}")
    lines.append(f"- **Blocking issues:** {n_blocking}")
    lines.append(f"- **Major issues:** {n_major}")
    lines.append(f"- **Minor issues:** {n_minor}")
    lines.append(f"- **Informational:** {n_info}")

    lines.append("\n## Per-Case Audit Flags\n")
    lines.append("| Case ID | Case Name | Dims Coded | Dims Missing | SQ | Flags | Severity |")
    lines.append("|---------|-----------|-----------|-------------|-----|-------|----------|")
    for _, row in audit_df.iterrows():
        cid = str(row.get("case_id", ""))
        cname = str(row.get("case_name", ""))[:40]
        nc = row.get("n_dimensions_coded", "")
        nm = row.get("n_dimensions_missing", "")
        sq = row.get("source_quality_score", "")
        flags = str(row.get("audit_flags", "none"))[:60]
        sev = str(row.get("audit_severity", ""))
        lines.append(f"| {cid} | {cname} | {nc} | {nm} | {sq} | {flags} | {sev} |")

    lines.append("\n## Classification Legend\n")
    lines.append("- **blocking**: case should not be included without correction")
    lines.append("- **major**: significant quality issue, review recommended")
    lines.append("- **minor**: small gap, flag for next coding round")
    lines.append("- **informational**: no action required")

    lines.append("\n## Validation Issues\n")
    if val_result.errors:
        for issue in val_result.errors:
            lines.append(f"- [ERROR] `{issue.rule_id}` {issue.field} ({issue.case_id}): {issue.message}")
    else:
        lines.append("No errors.")
    if val_result.warnings:
        lines.append("")
        for issue in val_result.warnings:
            lines.append(f"- [WARN] `{issue.rule_id}` {issue.field} ({issue.case_id}): {issue.message}")

    md = "\n".join(lines) + "\n"

    # ── JSON ──────────────────────────────────────────────────────────────────
    json_dict: dict = {
        "schema": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "generated": ts,
        "n_cases": n_cases,
        "validation_status": "pass" if val_result.is_valid else "fail",
        "n_validation_errors": len(val_result.errors),
        "n_validation_warnings": len(val_result.warnings),
        "n_blocking": n_blocking,
        "n_major": n_major,
        "n_minor": n_minor,
        "n_informational": n_info,
        "cases": audit_df.to_dict(orient="records"),
    }

    return md, json_dict


def build_artifact_manifest_md(manifest: dict) -> str:
    """
    Convert a JSON manifest dict (from build_artifact_manifest) into Markdown.

    Produces outputs/reports/manuscript_artifact_manifest.md.
    """
    lines: list[str] = []
    lines.append(f"# {PROJECT_NAME} v{PROJECT_VERSION} — Manuscript Artifact Manifest")
    lines.append(
        f"\n_Generated: {manifest.get('generated', '')}_ | "
        f"Dataset version: {manifest.get('dataset_version', '')} | "
        f"Package version: {manifest.get('version', '')}"
    )
    lines.append(f"\n**Command:** `{manifest.get('command', '')}`")
    lines.append(f"\n**Total artifacts:** {manifest.get('n_artifacts', 0)}")
    lines.append("\n---\n")

    lines.append("## Tables\n")
    lines.append("| Filename | Type | Exists | SHA256 (prefix) |")
    lines.append("|----------|------|--------|-----------------|")
    for a in manifest.get("artifacts", []):
        if a.get("type") == "table":
            fname = Path(a.get("path", "")).name
            exists = "✓" if a.get("exists") else "✗"
            sha = a.get("sha256_prefix", "—")
            lines.append(f"| `{fname}` | table | {exists} | `{sha}` |")

    lines.append("\n## Figures\n")
    lines.append("| Filename | Format | Exists | SHA256 (prefix) |")
    lines.append("|----------|--------|--------|-----------------|")
    for a in manifest.get("artifacts", []):
        if a.get("type") == "figure":
            fname = Path(a.get("path", "")).name
            fmt = a.get("format", "")
            exists = "✓" if a.get("exists") else "✗"
            sha = a.get("sha256_prefix", "—")
            lines.append(f"| `{fname}` | {fmt} | {exists} | `{sha}` |")

    lines.append("\n## Reports\n")
    lines.append("| Filename | Type | Exists | SHA256 (prefix) |")
    lines.append("|----------|------|--------|-----------------|")
    for a in manifest.get("artifacts", []):
        if a.get("type") == "report":
            fname = Path(a.get("path", "")).name
            exists = "✓" if a.get("exists") else "✗"
            sha = a.get("sha256_prefix", "—")
            lines.append(f"| `{fname}` | report | {exists} | `{sha}` |")

    lines.append("\n---\n")
    lines.append(
        "The artifact manifest in `outputs/reports/manuscript_artifact_manifest.json` "
        "records the filename, generation command, dataset version, and SHA256 hash of "
        "each table and figure used in the manuscript."
    )

    return "\n".join(lines) + "\n"


def build_reproducibility_report(
    n_cases: int,
    input_path: Optional[Path],
    outdir: Path,
    run_timestamp: Optional[str] = None,
) -> str:
    """
    Build a Markdown reproducibility report for outputs/reports/reproducibility_report.md.

    Records run metadata, package versions, and the command invoked.
    """
    import sys
    import importlib

    ts = run_timestamp or datetime.datetime.now().isoformat(timespec="seconds")

    lines: list[str] = []
    lines.append(f"# {PROJECT_NAME} v{PROJECT_VERSION} — Reproducibility Report")
    lines.append(f"\n_Generated: {ts}_\n")
    lines.append("> **Disclaimer:** " + DISCLAIMER)
    lines.append("\n---\n")

    lines.append("## Run Metadata\n")
    lines.append(f"- **Dataset version:** {PROJECT_VERSION}")
    lines.append(f"- **Cases processed:** {n_cases}")
    lines.append(f"- **Input file:** `{input_path}`")
    lines.append(f"- **Output root:** `{outdir}`")
    lines.append(f"- **Run timestamp:** {ts}")

    lines.append("\n## Command\n")
    lines.append(
        f"```\ncsa-lite all --input {input_path} --outdir {outdir}\n```"
    )

    lines.append("\n## Python Environment\n")
    lines.append(f"- **Python:** {sys.version}")
    pkg_list = ["pandas", "numpy", "matplotlib", "pydantic", "pandera", "typer", "rich"]
    for pkg in pkg_list:
        try:
            mod = importlib.import_module(pkg)
            ver = getattr(mod, "__version__", "unknown")
        except ImportError:
            ver = "not installed"
        lines.append(f"- **{pkg}:** {ver}")

    lines.append("\n## Expected Outputs\n")
    lines.append("### Tables\n")
    table_names = [
        "table_1_csalite_dimensions.csv",
        "table_2_corpus_composition_by_annex_area.csv",
        "table_3_within_category_variance.csv",
        "table_4_dimension_level_patterns.csv",
        "table_5_evidence_confidence_by_dimension.csv",
        "table_6_sensitivity_summary.csv",
        "table_7_matched_case_contrasts.csv",
    ]
    for t in table_names:
        p = outdir / "tables" / t
        status = "✓" if p.exists() else "✗"
        lines.append(f"- {status} `{t}`")

    lines.append("\n### Supplementary Tables\n")
    supp_table_names = [
        "supp_table_s1_full_case_corpus.csv",
        "supp_table_s2_scored_cases.csv",
        "supp_table_s3_sensitivity_per_case.csv",
        "supp_table_s4_sources_manifest.csv",
        "supp_table_s5_annex_mapping_rationales.csv",
        "supp_table_s6_validation_summary.csv",
        "supp_table_s7_case_audit_flags.csv",
    ]
    for t in supp_table_names:
        p = outdir / "tables" / t
        status = "✓" if p.exists() else "✗"
        lines.append(f"- {status} `{t}`")

    lines.append("\n### Figures\n")
    fig_stems = [
        "fig_1_pipeline_architecture",
        "fig_2_corpus_by_annex_area",
        "fig_3_context_severity_by_annex_area",
        "fig_4_dimension_heatmap",
        "fig_5_evidence_confidence_matrix",
        "fig_6_sensitivity_comparison",
    ]
    for stem in fig_stems:
        for ext in ("png", "svg"):
            p = outdir / "figures" / f"{stem}.{ext}"
            status = "✓" if p.exists() else "✗"
            lines.append(f"- {status} `{stem}.{ext}`")

    return "\n".join(lines) + "\n"


def build_artifact_manifest(
    outdir: Path,
    input_path: Optional[Path] = None,
    dataset_version: str = "0.2.0",
) -> dict:
    """
    Build a JSON-serialisable artifact manifest for outputs/reports/manuscript_artifact_manifest.json.

    Lists all expected output artifacts with their existence status,
    generated_from command, and dataset_version.
    """
    import hashlib

    def _file_hash(p: Path) -> Optional[str]:
        if not p.exists():
            return None
        h = hashlib.sha256()
        h.update(p.read_bytes())
        return h.hexdigest()[:16]

    generated = datetime.datetime.now().isoformat(timespec="seconds")
    command = f"csalite all --input {input_path} --outdir {outdir}"

    artifacts: list[dict] = []

    # Manuscript tables (1-7)
    table_names = [
        "table_1_csalite_dimensions.csv",
        "table_2_corpus_composition_by_annex_area.csv",
        "table_3_within_category_variance.csv",
        "table_4_dimension_level_patterns.csv",
        "table_5_evidence_confidence_by_dimension.csv",
        "table_6_sensitivity_summary.csv",
        "table_7_matched_case_contrasts.csv",
    ]
    for name in table_names:
        p = outdir / "tables" / name
        artifacts.append(
            {
                "path": str(p.relative_to(outdir.parent) if outdir.parent != outdir else p),
                "type": "table",
                "manuscript_label": name.replace(".csv", "").replace("_", " ").title(),
                "exists": p.exists(),
                "sha256_prefix": _file_hash(p),
                "generated_from": command,
                "dataset_version": dataset_version,
            }
        )

    # Supplementary tables (S1-S7)
    supp_table_names = [
        "supp_table_s1_full_case_corpus.csv",
        "supp_table_s2_scored_cases.csv",
        "supp_table_s3_sensitivity_per_case.csv",
        "supp_table_s4_sources_manifest.csv",
        "supp_table_s5_annex_mapping_rationales.csv",
        "supp_table_s6_validation_summary.csv",
        "supp_table_s7_case_audit_flags.csv",
    ]
    for name in supp_table_names:
        p = outdir / "tables" / name
        artifacts.append(
            {
                "path": str(p.relative_to(outdir.parent) if outdir.parent != outdir else p),
                "type": "table",
                "manuscript_label": name.replace(".csv", "").replace("_", " ").title(),
                "exists": p.exists(),
                "sha256_prefix": _file_hash(p),
                "generated_from": command,
                "dataset_version": dataset_version,
            }
        )

    # Figures (1-6, PNG + SVG)
    fig_stems = [
        "fig_1_pipeline_architecture",
        "fig_2_corpus_by_annex_area",
        "fig_3_context_severity_by_annex_area",
        "fig_4_dimension_heatmap",
        "fig_5_evidence_confidence_matrix",
        "fig_6_sensitivity_comparison",
    ]
    for stem in fig_stems:
        for ext in ("png", "svg"):
            p = outdir / "figures" / f"{stem}.{ext}"
            artifacts.append(
                {
                    "path": str(p.relative_to(outdir.parent) if outdir.parent != outdir else p),
                    "type": "figure",
                    "format": ext,
                    "manuscript_label": stem.replace("_", " ").title(),
                    "exists": p.exists(),
                    "sha256_prefix": _file_hash(p),
                    "generated_from": command,
                    "dataset_version": dataset_version,
                }
            )

    # Reports (self-referencing manifest files are excluded — they cannot exist
    # at manifest-build time; they are written after this function returns)
    report_names = [
        "validation_report.md",
        "validation_report.json",
        "reproducibility_report.md",
        "reproducibility_report.json",
        "scoring_summary.md",
        "case_audit_report.md",
        "case_audit_report.json",
    ]
    for name in report_names:
        p = outdir / "reports" / name
        artifacts.append(
            {
                "path": str(p.relative_to(outdir.parent) if outdir.parent != outdir else p),
                "type": "report",
                "exists": p.exists(),
                "sha256_prefix": _file_hash(p),
                "generated_from": command,
                "dataset_version": dataset_version,
            }
        )

    return {
        "schema": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "dataset_version": dataset_version,
        "generated": generated,
        "command": command,
        "n_artifacts": len(artifacts),
        "artifacts": artifacts,
    }

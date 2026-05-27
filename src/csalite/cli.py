"""
CSA-lite command-line interface.

Entry point: `csalite`

Commands:
  validate     -- Validate a cases CSV/JSONL against rules and schema
  score        -- Compute scoring fields and write scored_cases CSV/JSONL
  analyze      -- Generate analysis tables (Tables 1–8)
  figures      -- Generate manuscript figures (Figs 1–6)
  sensitivity  -- Generate sensitivity analysis
  audit-cases  -- Generate case audit report
  report       -- Generate a combined Markdown report
  manifest     -- Generate artifact manifest
  all          -- Run full pipeline: validate → score → analyze → supplementary
                  → figures → sensitivity → case audit → report → manifest
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from csalite import __version__
from csalite.constants import DISCLAIMER

app = typer.Typer(
    name="csalite",
    help=(
        "CSA-Lite: Context-Sliced AI Assurance Lite — "
        "reproducible public-records risk analysis framework.\n\n"
        f"v{__version__}\n\n"
        "DISCLAIMER: " + DISCLAIMER
    ),
    add_completion=False,
)

console = Console()


def _load_df(input_path: Path):  # type: ignore[return]
    from csalite.io import read_cases_csv, read_cases_jsonl

    suffix = input_path.suffix.lower()
    if suffix == ".jsonl":
        return read_cases_jsonl(input_path)
    elif suffix == ".csv":
        return read_cases_csv(input_path)
    else:
        console.print(f"[red]Unknown file extension: {suffix}. Expected .csv or .jsonl[/red]")
        raise typer.Exit(code=1)


# ── validate ──────────────────────────────────────────────────────────────────


@app.command()
def validate(
    input: Path = typer.Option(..., "--input", "-i", help="Input cases CSV or JSONL"),
    schema: Optional[Path] = typer.Option(None, "--schema", "-s", help="JSON schema file to validate against"),
    report: Optional[Path] = typer.Option(None, "--report", "-r", help="Output Markdown report path"),
) -> None:
    """Validate a cases file against CSA-lite rules (and optionally a JSON schema)."""
    from csalite.io import load_json_schema, validate_dataframe_against_schema
    from csalite.reporting import build_validation_report, write_report
    from csalite.validation import validate_dataframe

    console.print(f"[bold]CSA-Lite Validator v{__version__}[/bold]")
    console.print(f"Input: {input}")

    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(code=1)

    df = _load_df(input)
    n_cases = len(df)
    console.print(f"Loaded {n_cases} cases.")

    result = validate_dataframe(df)

    # Print summary
    status_style = "green" if result.is_valid else "red"
    console.print(f"[{status_style}]{result.summary()}[/{status_style}]")

    if result.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for issue in result.errors[:20]:
            console.print(f"  [red]•[/red] [{issue.rule_id}] {issue.field} ({issue.case_id}): {issue.message}")
        if len(result.errors) > 20:
            console.print(f"  ... and {len(result.errors) - 20} more errors")

    if result.warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for issue in result.warnings[:10]:
            console.print(f"  [yellow]•[/yellow] [{issue.rule_id}] {issue.field}: {issue.message}")

    # Schema validation
    if schema:
        if not schema.exists():
            console.print(f"[red]Schema file not found: {schema}[/red]")
        else:
            json_schema = load_json_schema(schema)
            schema_errors = validate_dataframe_against_schema(df, json_schema)
            if schema_errors:
                console.print(f"\n[bold red]Schema errors ({len(schema_errors)} cases):[/bold red]")
                for case_id, errs in list(schema_errors.items())[:5]:
                    console.print(f"  [red]{case_id}:[/red]")
                    for e in errs[:3]:
                        console.print(f"    • {e}")
            else:
                console.print("[green]Schema validation passed.[/green]")

    # Write report
    if report:
        md = build_validation_report(result, input_path=input, n_cases=n_cases)
        write_report(md, report)
        console.print(f"[green]Report written to: {report}[/green]")

    raise typer.Exit(code=0 if result.is_valid else 1)


# ── score ─────────────────────────────────────────────────────────────────────


@app.command()
def score(
    input: Path = typer.Option(..., "--input", "-i", help="Input cases CSV or JSONL"),
    output: Path = typer.Option(..., "--output", "-o", help="Output scored CSV path"),
    jsonl_output: Optional[Path] = typer.Option(None, "--jsonl-output", help="Output scored JSONL path"),
) -> None:
    """Compute CSA-lite scoring fields and write a scored cases file."""
    from csalite.io import write_cases_csv, write_cases_jsonl
    from csalite.scoring import score_dataframe

    console.print(f"[bold]CSA-Lite Scorer v{__version__}[/bold]")

    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(code=1)

    df = _load_df(input)
    console.print(f"Loaded {len(df)} cases.")

    scored = score_dataframe(df)
    write_cases_csv(scored, output)
    console.print(f"[green]Scored CSV written to: {output}[/green]")

    if jsonl_output:
        write_cases_jsonl(scored, jsonl_output)
        console.print(f"[green]Scored JSONL written to: {jsonl_output}[/green]")

    # Print summary
    if "context_severity_band" in scored.columns:
        band_counts = scored["context_severity_band"].value_counts()
        t = Table(title="CSI Band Distribution", show_header=True)
        t.add_column("Band")
        t.add_column("Count", justify="right")
        for band in ["low", "moderate", "high", "severe", "unknown"]:
            t.add_row(band, str(int(band_counts.get(band, 0))))
        console.print(t)


# ── analyze ───────────────────────────────────────────────────────────────────


@app.command()
def analyze(
    input: Path = typer.Option(..., "--input", "-i", help="Scored cases CSV or JSONL"),
    outdir: Path = typer.Option(..., "--outdir", "-d", help="Output directory for tables"),
) -> None:
    """Generate all 8 analysis tables from a scored cases file."""
    from csalite.analysis import compute_all_tables
    from csalite.io import write_table_csv

    console.print(f"[bold]CSA-Lite Analysis v{__version__}[/bold]")

    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(code=1)

    df = _load_df(input)
    console.print(f"Loaded {len(df)} cases.")

    outdir.mkdir(parents=True, exist_ok=True)
    tables = compute_all_tables(df)

    for name, table_df in tables.items():
        path = outdir / f"{name}.csv"
        write_table_csv(table_df, path)
        console.print(f"  [green]✓[/green] {name}.csv ({len(table_df)} rows)")

    console.print(f"[green]Tables written to: {outdir}[/green]")


# ── figures ───────────────────────────────────────────────────────────────────


@app.command()
def figures(
    input: Path = typer.Option(..., "--input", "-i", help="Scored cases CSV or JSONL"),
    outdir: Path = typer.Option(..., "--outdir", "-d", help="Output directory for figures"),
) -> None:
    """Generate all 6 manuscript figures."""
    from csalite.plots import generate_all_figures

    console.print(f"[bold]CSA-Lite Figures v{__version__}[/bold]")

    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(code=1)

    df = _load_df(input)
    console.print(f"Loaded {len(df)} cases.")
    outdir.mkdir(parents=True, exist_ok=True)

    try:
        figs = generate_all_figures(df, outdir)
        console.print(f"[green]Generated {len(figs)} figures in: {outdir}[/green]")
    except ValueError as exc:
        console.print(f"[yellow]Warning: {exc}[/yellow]")
        raise typer.Exit(code=1)


# ── sensitivity ───────────────────────────────────────────────────────────────


@app.command()
def sensitivity(
    input: Path = typer.Option(..., "--input", "-i", help="Cases CSV or JSONL (scored or raw)"),
    outdir: Path = typer.Option(..., "--outdir", "-d", help="Output directory"),
) -> None:
    """Generate sensitivity analysis table and summary."""
    from csalite.io import write_table_csv
    from csalite.sensitivity import compute_band_change_summary, compute_sensitivity_dataframe

    console.print(f"[bold]CSA-Lite Sensitivity v{__version__}[/bold]")

    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(code=1)

    df = _load_df(input)
    outdir.mkdir(parents=True, exist_ok=True)

    sens_df = compute_sensitivity_dataframe(df)
    write_table_csv(sens_df, outdir / "sensitivity_detail.csv")

    summary_df = compute_band_change_summary(sens_df)
    write_table_csv(summary_df, outdir / "sensitivity_summary.csv")

    n_changes = int(sens_df["sensitivity_band_change"].sum()) if not sens_df.empty else 0
    console.print(
        f"[green]Sensitivity analysis complete: {n_changes}/{len(sens_df)} cases "
        f"show band changes across imputation assumptions.[/green]"
    )


# ── report ────────────────────────────────────────────────────────────────────


@app.command()
def report(
    input: Path = typer.Option(..., "--input", "-i", help="Scored cases CSV or JSONL"),
    validation: Optional[Path] = typer.Option(None, "--validation", "-v", help="Pre-computed validation report MD"),
    out: Path = typer.Option(..., "--out", "-o", help="Output Markdown report path"),
) -> None:
    """Generate a combined scoring summary Markdown report."""
    from csalite.reporting import build_scoring_summary_report, write_report
    from csalite.validation import validate_dataframe

    console.print(f"[bold]CSA-Lite Report v{__version__}[/bold]")

    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(code=1)

    df = _load_df(input)
    val_result = validate_dataframe(df)
    md = build_scoring_summary_report(df, validation_result=val_result)
    write_report(md, out)
    console.print(f"[green]Report written to: {out}[/green]")


# ── audit-cases ───────────────────────────────────────────────────────────────


@app.command(name="audit-cases")
def audit_cases(
    input: Path = typer.Option(..., "--input", "-i", help="Input cases CSV or JSONL"),
    scored: Optional[Path] = typer.Option(None, "--scored", "-s", help="Pre-scored cases CSV (optional)"),
    outdir: Path = typer.Option(..., "--outdir", "-d", help="Output directory for audit reports"),
) -> None:
    """Generate case audit report (MD + JSON) and supp_table_s7_case_audit_flags.csv."""
    import json as _json
    from csalite.reporting import build_case_audit_report, write_report
    from csalite.scoring import score_dataframe
    from csalite.io import write_table_csv
    from csalite.analysis import supp_table_s7_case_audit_flags

    console.print(f"[bold]CSA-Lite Case Audit v{__version__}[/bold]")

    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(code=1)

    df = _load_df(input)
    if scored and scored.exists():
        df_scored = _load_df(scored)
    else:
        df_scored = score_dataframe(df)

    reports_dir = outdir / "reports"
    tables_dir = outdir / "tables"
    reports_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    audit_md, audit_json = build_case_audit_report(df_scored)
    write_report(audit_md, reports_dir / "case_audit_report.md")
    (reports_dir / "case_audit_report.json").write_text(
        _json.dumps(audit_json, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    flags_df = supp_table_s7_case_audit_flags(df_scored)
    write_table_csv(flags_df, tables_dir / "supp_table_s7_case_audit_flags.csv")

    console.print(f"[green]Case audit report written to: {reports_dir}[/green]")
    console.print(f"[green]Case audit flags table written to: {tables_dir}[/green]")


# ── manifest ──────────────────────────────────────────────────────────────────


@app.command()
def manifest(
    out: Path = typer.Option(..., "--out", "-o", help="Output JSON manifest path"),
    outdir: Path = typer.Option(Path("outputs"), "--outdir", "-d", help="Root output directory to inspect"),
    input: Path = typer.Option(Path("data/processed/csa_lite_cases.csv"), "--input", "-i", help="Input cases CSV"),
) -> None:
    """Generate artifact manifest (JSON + MD) for all pipeline outputs."""
    import json as _json
    from csalite.reporting import build_artifact_manifest, build_artifact_manifest_md, write_report

    console.print(f"[bold]CSA-Lite Manifest v{__version__}[/bold]")

    mf = build_artifact_manifest(outdir=outdir, input_path=input, dataset_version="0.2.0")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_json.dumps(mf, indent=2, ensure_ascii=False), encoding="utf-8")
    console.print(f"[green]Manifest JSON written to: {out}[/green]")

    md_path = out.with_suffix(".md")
    write_report(build_artifact_manifest_md(mf), md_path)
    console.print(f"[green]Manifest MD written to: {md_path}[/green]")


# ── all ───────────────────────────────────────────────────────────────────────


@app.command()
def all(
    input: Path = typer.Option(..., "--input", "-i", help="Input cases CSV or JSONL"),
    outdir: Path = typer.Option(..., "--outdir", "-d", help="Root output directory"),
) -> None:
    """Run the full CSA-lite pipeline: validate, score, analyze, figures, sensitivity, report.

    Also writes:
      outputs/reports/validation_report.json
      outputs/reports/reproducibility_report.md
      outputs/reports/reproducibility_report.json
      outputs/reports/case_audit_report.md
      outputs/reports/case_audit_report.json
      outputs/reports/manuscript_artifact_manifest.json
      outputs/reports/manuscript_artifact_manifest.md
      outputs/tables/supp_table_s1_full_case_corpus.csv
      outputs/tables/supp_table_s2_scored_cases.csv
      outputs/tables/supp_table_s3_sensitivity_per_case.csv
      outputs/tables/supp_table_s4_sources_manifest.csv
      outputs/tables/supp_table_s5_annex_mapping_rationales.csv
      outputs/tables/supp_table_s6_validation_summary.csv
      outputs/tables/supp_table_s7_case_audit_flags.csv

    Scored cases are written both to <outdir>/scored_cases.csv and
    to <input_dir>/scored_cases.csv (i.e. data/processed/scored_cases.csv).
    """
    import json as _json
    from csalite.analysis import compute_all_tables, compute_all_supplementary_tables
    from csalite.io import write_cases_csv, write_cases_jsonl, write_table_csv
    from csalite.plots import generate_all_figures
    from csalite.reporting import (
        build_validation_report,
        build_validation_report_json,
        build_scoring_summary_report,
        build_reproducibility_report,
        build_reproducibility_report_json,
        build_case_audit_report,
        build_artifact_manifest,
        build_artifact_manifest_md,
        write_report,
    )
    from csalite.scoring import score_dataframe
    from csalite.sensitivity import compute_sensitivity_dataframe
    from csalite.validation import validate_dataframe

    console.print(f"[bold]CSA-Lite Full Pipeline v{__version__}[/bold]")
    console.print(f"Input: {input}")
    console.print(f"Output root: {outdir}")

    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(code=1)

    outdir.mkdir(parents=True, exist_ok=True)
    tables_dir = outdir / "tables"
    figures_dir = outdir / "figures"
    reports_dir = outdir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    df = _load_df(input)
    n_cases = len(df)
    console.print(f"Loaded {n_cases} cases.")

    # 1. Validate
    console.rule("Step 1: Validate")
    val_result = validate_dataframe(df)
    val_md = build_validation_report(val_result, input_path=input, n_cases=n_cases)
    write_report(val_md, reports_dir / "validation_report.md")

    val_json = build_validation_report_json(val_result, n_cases=n_cases, input_path=input)
    (reports_dir / "validation_report.json").write_text(
        _json.dumps(val_json, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    status_style = "green" if val_result.is_valid else "yellow"
    console.print(f"[{status_style}]{val_result.summary()}[/{status_style}]")

    # 2. Score
    console.rule("Step 2: Score")
    scored = score_dataframe(df)
    write_cases_csv(scored, outdir / "scored_cases.csv")
    write_cases_jsonl(scored, outdir / "scored_cases.jsonl")

    # Also write scored_cases to data/processed/ alongside the input file
    data_processed_scored = input.parent / "scored_cases.csv"
    write_cases_csv(scored, data_processed_scored)
    console.print(f"[green]Scored {len(scored)} cases[/green]")
    console.print(f"  ↳ Also written to: {data_processed_scored}")

    # 3. Analyze — manuscript tables (1–8)
    console.rule("Step 3: Analyze (manuscript tables)")
    tables = compute_all_tables(scored)
    for name, tdf in tables.items():
        write_table_csv(tdf, tables_dir / f"{name}.csv")
    console.print(f"[green]Generated {len(tables)} manuscript tables[/green]")

    # 3b. Supplementary tables (S1–S7)
    console.rule("Step 3b: Supplementary Tables")
    supp_tables = compute_all_supplementary_tables(scored)
    for name, tdf in supp_tables.items():
        write_table_csv(tdf, tables_dir / f"{name}.csv")
    console.print(f"[green]Generated {len(supp_tables)} supplementary tables[/green]")

    # 4. Figures
    console.rule("Step 4: Figures")
    try:
        figs = generate_all_figures(scored, figures_dir)
        console.print(f"[green]Generated {len(figs)} figures[/green]")
    except ValueError as exc:
        console.print(f"[yellow]Figures skipped: {exc}[/yellow]")

    # 5. Sensitivity (supplementary detail)
    console.rule("Step 5: Sensitivity")
    sens_df = compute_sensitivity_dataframe(scored)
    write_table_csv(sens_df, tables_dir / "sensitivity_detail.csv")
    console.print("[green]Sensitivity detail written[/green]")

    # 6. Case audit
    console.rule("Step 6: Case Audit")
    audit_md, audit_json = build_case_audit_report(scored)
    write_report(audit_md, reports_dir / "case_audit_report.md")
    (reports_dir / "case_audit_report.json").write_text(
        _json.dumps(audit_json, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    console.print("[green]Case audit report written[/green]")

    # 7. Reports
    console.rule("Step 7: Reports")
    summary_md = build_scoring_summary_report(scored, validation_result=val_result)
    write_report(summary_md, reports_dir / "scoring_summary.md")

    repro_md = build_reproducibility_report(
        n_cases=n_cases,
        input_path=input,
        outdir=outdir,
    )
    write_report(repro_md, reports_dir / "reproducibility_report.md")

    repro_json = build_reproducibility_report_json(
        n_cases=n_cases,
        input_path=input,
        outdir=outdir,
        validation_result=val_result,
    )
    (reports_dir / "reproducibility_report.json").write_text(
        _json.dumps(repro_json, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # 8. Artifact manifest (JSON + MD)
    console.rule("Step 8: Artifact Manifest")
    manifest = build_artifact_manifest(
        outdir=outdir,
        input_path=input,
        dataset_version="0.2.0",
    )
    (reports_dir / "manuscript_artifact_manifest.json").write_text(
        _json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    manifest_md = build_artifact_manifest_md(manifest)
    write_report(manifest_md, reports_dir / "manuscript_artifact_manifest.md")

    console.print(f"[green]Reports written to: {reports_dir}[/green]")

    console.rule("Done")
    console.print(f"[bold green]Pipeline complete. Outputs in: {outdir}[/bold green]")


# ── version ───────────────────────────────────────────────────────────────────


@app.command()
def version() -> None:
    """Print CSA-lite version."""
    console.print(f"CSA-Lite v{__version__}")


if __name__ == "__main__":
    app()

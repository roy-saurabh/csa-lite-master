"""
Figure generation for CSA-lite manuscript.

Produces 6 figures, each saved in both PNG and SVG formats.
Uses matplotlib ONLY — no seaborn.

Figure function names:
  plot_pipeline_architecture(outdir)           → fig_1_pipeline_architecture
  plot_corpus_by_annex_area(df, outdir)        → fig_2_corpus_by_annex_area
  plot_context_severity_by_annex_area(df, outdir) → fig_3_context_severity_by_annex_area
  plot_dimension_heatmap(df, outdir)           → fig_4_dimension_heatmap
  plot_evidence_confidence_matrix(df, outdir)  → fig_5_evidence_confidence_matrix
  plot_sensitivity_comparison(df, outdir)      → fig_6_sensitivity_comparison

All figure functions:
  - Raise ValueError for empty datasets
  - Accept an outdir parameter (pathlib.Path)
  - Save both .png and .svg
  - Return the Figure object
  - Use RANDOM_SEED for jitter reproducibility
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

matplotlib.use("Agg")  # non-interactive backend

from csalite.constants import FIGURE_DPI, FIGURE_FORMATS, RANDOM_SEED, SCORE_DIMENSIONS
from csalite.enums import SeverityBand

# Colour palette (accessible, matplotlib-compatible)
_BAND_COLOURS = {
    "low": "#4CAF50",
    "moderate": "#FFC107",
    "high": "#FF5722",
    "severe": "#B71C1C",
    "unknown": "#9E9E9E",
}
_DIM_SCORE_COLOURS = {0: "#4CAF50", 1: "#FFC107", 2: "#F44336", "missing": "#E0E0E0"}
_CONF_COLOURS = {
    "high": "#1565C0",
    "medium": "#42A5F5",
    "low": "#90CAF9",
    "missing": "#E0E0E0",
}


def _save_figure(fig: plt.Figure, outdir: Path, stem: str) -> None:
    """Save figure in all configured formats."""
    outdir.mkdir(parents=True, exist_ok=True)
    for fmt in FIGURE_FORMATS:
        fig.savefig(outdir / f"{stem}.{fmt}", dpi=FIGURE_DPI, bbox_inches="tight")


def _require_nonempty(df: pd.DataFrame, context: str) -> None:
    if df is None or df.empty:
        raise ValueError(f"Empty dataset provided to {context}; cannot generate figure")


# ── Figure 1 ──────────────────────────────────────────────────────────────────


def plot_pipeline_architecture(outdir: Path) -> plt.Figure:
    """
    Fig 1: CSA-lite pipeline architecture diagram (text boxes + arrows).
    Saved as fig_1_pipeline_architecture.{png,svg}.
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_facecolor("#FAFAFA")
    fig.patch.set_facecolor("#FAFAFA")

    steps = [
        (5, 7.0, "Public Record\nCollection", "#E3F2FD"),
        (5, 5.7, "Case Identification\n& Source Quality Rating", "#E8F5E9"),
        (5, 4.4, "Structured Coding\n(8 Dimensions × 0–2)", "#FFF9C4"),
        (5, 3.1, "Scoring &\nSensitivity Analysis", "#FBE9E7"),
        (5, 1.8, "Analysis Tables\n& Figures", "#EDE7F6"),
        (5, 0.5, "Reproducible Archive\n(CSV / JSONL / Schemas)", "#E0F2F1"),
    ]

    box_w, box_h = 4.5, 0.8
    for x, y, label, colour in steps:
        rect = mpatches.FancyBboxPatch(
            (x - box_w / 2, y - box_h / 2),
            box_w, box_h,
            boxstyle="round,pad=0.1",
            facecolor=colour,
            edgecolor="#555",
            linewidth=1.2,
        )
        ax.add_patch(rect)
        ax.text(
            x, y, label,
            ha="center", va="center",
            fontsize=9, fontweight="bold", color="#222",
        )

    arrow_props = dict(arrowstyle="-|>", color="#555", lw=1.5)
    for i in range(len(steps) - 1):
        _, y_from, _, _ = steps[i]
        _, y_to, _, _ = steps[i + 1]
        ax.annotate(
            "",
            xy=(5, y_to + box_h / 2),
            xytext=(5, y_from - box_h / 2),
            arrowprops=arrow_props,
        )

    ax.text(
        5, -0.3,
        "CSA-lite does not produce legal classifications or compliance determinations.",
        ha="center", va="center", fontsize=7, color="#666", style="italic",
    )
    ax.set_title("CSA-lite Analysis Pipeline Architecture", fontsize=12, fontweight="bold", pad=10)

    _save_figure(fig, outdir, "fig_1_pipeline_architecture")
    plt.close(fig)
    return fig


# ── Figure 2 ──────────────────────────────────────────────────────────────────


def plot_corpus_by_annex_area(df: pd.DataFrame, outdir: Path) -> plt.Figure:
    """
    Fig 2: Bar chart of case counts by Annex III area.
    Saved as fig_2_corpus_by_annex_area.{png,svg}.
    """
    _require_nonempty(df, "plot_corpus_by_annex_area")

    counts = df["annex_iii_area"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(
        range(len(counts)),
        counts.values,
        color="#42A5F5",
        edgecolor="#1565C0",
        linewidth=0.8,
    )
    ax.set_xticks(range(len(counts)))
    ax.set_xticklabels(
        [s.replace("_", "\n") for s in counts.index],
        fontsize=8, rotation=0, ha="center",
    )
    ax.set_xlabel("EU AI Act Annex III Area (analytical reference frame)", fontsize=10)
    ax.set_ylabel("Number of cases", fontsize=10)
    ax.set_title("Corpus Composition by Annex III Analytical Area", fontsize=12, fontweight="bold")

    for bar, val in zip(bars, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.1,
            str(val),
            ha="center", va="bottom", fontsize=9,
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    _save_figure(fig, outdir, "fig_2_corpus_by_annex_area")
    plt.close(fig)
    return fig


# ── Figure 3 ──────────────────────────────────────────────────────────────────


def plot_context_severity_by_annex_area(df: pd.DataFrame, outdir: Path) -> plt.Figure:
    """
    Fig 3: Boxplot with jitter of CSI by Annex III area.
    Saved as fig_3_context_severity_by_annex_area.{png,svg}.
    """
    _require_nonempty(df, "plot_context_severity_by_annex_area")
    if "context_severity_index" not in df.columns:
        raise ValueError("context_severity_index column required for Fig 3")

    rng = np.random.default_rng(RANDOM_SEED)
    areas = sorted(df["annex_iii_area"].dropna().unique())
    n = len(areas)

    fig, ax = plt.subplots(figsize=(max(8, n * 1.2), 6))
    area_data = []
    for area in areas:
        csi = pd.to_numeric(
            df[df["annex_iii_area"] == area]["context_severity_index"],
            errors="coerce",
        ).dropna().tolist()
        area_data.append(csi)

    bp = ax.boxplot(
        area_data,
        positions=range(n),
        patch_artist=True,
        widths=0.5,
        boxprops=dict(facecolor="#BBDEFB", color="#1565C0"),
        medianprops=dict(color="#B71C1C", linewidth=2),
        whiskerprops=dict(color="#1565C0"),
        capprops=dict(color="#1565C0"),
        flierprops=dict(marker="o", color="#1565C0", alpha=0.5, markersize=4),
    )

    for i, csi_vals in enumerate(area_data):
        if csi_vals:
            jitter = rng.uniform(-0.18, 0.18, size=len(csi_vals))
            ax.scatter(
                [i + j for j in jitter],
                csi_vals,
                alpha=0.6,
                s=25,
                color="#F57C00",
                zorder=3,
            )

    ax.set_xticks(range(n))
    ax.set_xticklabels(
        [a.replace("_", "\n") for a in areas],
        fontsize=8, rotation=0, ha="center",
    )
    ax.set_xlabel("EU AI Act Annex III Area (analytical reference frame)", fontsize=10)
    ax.set_ylabel("Context Severity Index (CSI, neutral imputation)", fontsize=10)
    ax.set_title(
        "Context Severity Index by Annex III Analytical Area\n"
        "(CSI is a structured-coding output, NOT a legal risk class)",
        fontsize=11, fontweight="bold",
    )
    ax.set_ylim(-0.5, 16.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    _save_figure(fig, outdir, "fig_3_context_severity_by_annex_area")
    plt.close(fig)
    return fig


# ── Figure 4 ──────────────────────────────────────────────────────────────────


def plot_dimension_heatmap(df: pd.DataFrame, outdir: Path) -> plt.Figure:
    """
    Fig 4: Heatmap of dimension scores (rows=cases, cols=dimensions).
    Values: 0=green, 1=amber, 2=red, missing=grey.
    Saved as fig_4_dimension_heatmap.{png,svg}.
    """
    _require_nonempty(df, "plot_dimension_heatmap")

    df_sorted = df.sort_values("case_id").reset_index(drop=True)
    n_cases = len(df_sorted)
    n_dims = len(SCORE_DIMENSIONS)

    matrix = np.full((n_cases, n_dims), np.nan)
    for i, (_, row) in enumerate(df_sorted.iterrows()):
        for j, dim in enumerate(SCORE_DIMENSIONS):
            val = row.get(f"{dim}_score")
            try:
                iv = int(val)
                if iv in (0, 1, 2):
                    matrix[i, j] = iv
            except (TypeError, ValueError):
                pass

    cmap = matplotlib.colormaps.get_cmap("RdYlGn_r")
    cmap.set_bad(color="#BDBDBD")

    display = np.where(np.isnan(matrix), np.nan, matrix / 2.0)

    fig_h = max(4, n_cases * 0.35)
    fig, ax = plt.subplots(figsize=(max(8, n_dims * 1.2), fig_h))

    im = ax.imshow(
        display,
        aspect="auto",
        cmap=cmap,
        vmin=0, vmax=1,
        interpolation="nearest",
    )
    ax.set_xticks(range(n_dims))
    ax.set_xticklabels(
        [d.replace("_", "\n") for d in SCORE_DIMENSIONS],
        fontsize=8,
    )
    ax.set_yticks(range(n_cases))
    labels = df_sorted.get("short_label", df_sorted.get("case_id", pd.Series(range(n_cases))))
    ax.set_yticklabels(labels, fontsize=7)

    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_ticks([0, 0.5, 1.0])
    cbar.set_ticklabels(["0 (low)", "1 (med)", "2 (high)"])
    cbar.set_label("Score", fontsize=8)

    ax.set_title(
        "CSA-lite Dimension Score Heatmap",
        fontsize=11, fontweight="bold",
    )
    fig.tight_layout()

    _save_figure(fig, outdir, "fig_4_dimension_heatmap")
    plt.close(fig)
    return fig


# ── Figure 5 ──────────────────────────────────────────────────────────────────


def plot_evidence_confidence_matrix(df: pd.DataFrame, outdir: Path) -> plt.Figure:
    """
    Fig 5: Evidence-confidence matrix (rows=cases, cols=dimensions).

    Colour-codes each cell by the evidence confidence level:
      high=dark blue, medium=mid blue, low=light blue, missing/unknown=grey.
    Saved as fig_5_evidence_confidence_matrix.{png,svg}.
    """
    _require_nonempty(df, "plot_evidence_confidence_matrix")

    df_sorted = df.sort_values("case_id").reset_index(drop=True)
    n_cases = len(df_sorted)
    n_dims = len(SCORE_DIMENSIONS)

    conf_to_num = {"high": 3, "medium": 2, "low": 1, "unknown": 0}
    matrix = np.zeros((n_cases, n_dims))

    for i, (_, row) in enumerate(df_sorted.iterrows()):
        for j, dim in enumerate(SCORE_DIMENSIONS):
            score_val = row.get(f"{dim}_score")
            is_missing = True
            try:
                iv = int(score_val)
                if iv in (0, 1, 2):
                    is_missing = False
            except (TypeError, ValueError):
                pass

            if is_missing:
                matrix[i, j] = -1  # missing
            else:
                conf = str(row.get(f"{dim}_confidence", "unknown")).strip().lower()
                matrix[i, j] = conf_to_num.get(conf, 0)

    colours = ["#BDBDBD", "#90CAF9", "#42A5F5", "#1565C0", "#0D47A1"]
    # -1=missing, 0=unknown, 1=low, 2=medium, 3=high
    from matplotlib.colors import BoundaryNorm, ListedColormap

    cmap = ListedColormap(colours)
    bounds = [-1.5, -0.5, 0.5, 1.5, 2.5, 3.5]
    norm = BoundaryNorm(bounds, cmap.N)

    fig_h = max(4, n_cases * 0.35)
    fig, ax = plt.subplots(figsize=(max(8, n_dims * 1.2), fig_h))

    im = ax.imshow(matrix, aspect="auto", cmap=cmap, norm=norm, interpolation="nearest")
    ax.set_xticks(range(n_dims))
    ax.set_xticklabels([d.replace("_", "\n") for d in SCORE_DIMENSIONS], fontsize=8)
    ax.set_yticks(range(n_cases))
    labels = df_sorted.get("short_label", df_sorted.get("case_id", pd.Series(range(n_cases))))
    ax.set_yticklabels(labels, fontsize=7)

    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04, ticks=[-1, 0, 1, 2, 3])
    cbar.set_ticklabels(["missing", "unknown", "low conf.", "med. conf.", "high conf."])
    cbar.set_label("Evidence Confidence", fontsize=8)

    ax.set_title(
        "Evidence Confidence Matrix by Case and Dimension\n(blue intensity = confidence; grey = missing score)",
        fontsize=11, fontweight="bold",
    )
    fig.tight_layout()

    _save_figure(fig, outdir, "fig_5_evidence_confidence_matrix")
    plt.close(fig)
    return fig


# ── Figure 6 ──────────────────────────────────────────────────────────────────


def plot_sensitivity_comparison(df: pd.DataFrame, outdir: Path) -> plt.Figure:
    """
    Fig 6: Sensitivity comparison — CSI under zero vs conservative assumptions.

    Scatter plot: x = CSI (zero/optimistic assumption),
                  y = CSI (conservative assumption).
    Points on the y=x diagonal indicate no sensitivity to unknown handling.
    Coloured by neutral-assumption severity band.
    Saved as fig_6_sensitivity_comparison.{png,svg}.
    """
    _require_nonempty(df, "plot_sensitivity_comparison")

    required = {"unknown_as_zero_score", "unknown_as_neutral_band", "unknown_as_conservative_score"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing sensitivity columns for Fig 6: {required - set(df.columns)}")

    x = pd.to_numeric(df["unknown_as_zero_score"], errors="coerce")
    y = pd.to_numeric(df["unknown_as_conservative_score"], errors="coerce")
    bands = df["unknown_as_neutral_band"].fillna("unknown")

    fig, ax = plt.subplots(figsize=(7, 7))

    for band, colour in _BAND_COLOURS.items():
        mask = bands == band
        if mask.any():
            ax.scatter(
                x[mask], y[mask],
                c=colour,
                label=f"{band} (n={int(mask.sum())})",
                s=60,
                alpha=0.85,
                edgecolors="#333",
                linewidths=0.5,
                zorder=3,
            )

    # y = x reference diagonal (no sensitivity)
    lim_min = min(float(x.min()), float(y.min())) - 0.5
    lim_max = max(float(x.max()), float(y.max())) + 0.5
    diag = np.linspace(lim_min, lim_max, 100)
    ax.plot(diag, diag, color="#888", linestyle="--", linewidth=1.2, label="No sensitivity (y=x)", zorder=2)

    ax.set_xlim(lim_min, lim_max)
    ax.set_ylim(lim_min, lim_max)
    ax.set_xlabel("CSI — null as 0 (optimistic)", fontsize=10)
    ax.set_ylabel("CSI — null as 2 (conservative)", fontsize=10)
    ax.set_title(
        "Sensitivity Comparison Across Missing-Value Rules\n"
        "(Points on diagonal = no band sensitivity to unknown-handling rule)",
        fontsize=11, fontweight="bold",
    )
    ax.legend(fontsize=8, title="Neutral-rule band", title_fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    total = int(mask.sum() * 0)  # reset; check all-on-diagonal
    n_off_diagonal = int(((x - y).abs() > 0).sum())
    note = (
        f"All {len(df)} cases on diagonal (no unknown values in v0.2.0 corpus)"
        if n_off_diagonal == 0
        else f"{n_off_diagonal}/{len(df)} cases off diagonal (CSI changes with imputation)"
    )
    ax.text(
        0.02, 0.97, note,
        transform=ax.transAxes,
        fontsize=7, color="#555", va="top", style="italic",
    )

    fig.tight_layout()

    _save_figure(fig, outdir, "fig_6_sensitivity_comparison")
    plt.close(fig)
    return fig


# ── All figures ────────────────────────────────────────────────────────────────


def generate_all_figures(df: pd.DataFrame, outdir: Path) -> dict[str, plt.Figure]:
    """
    Generate all 6 manuscript figures. Fig 1 has no data dependency.

    Raises ValueError if df is empty (for figs 2-6).
    Returns dict of figure name -> Figure object.
    """
    figs: dict[str, plt.Figure] = {}
    figs["fig_1"] = plot_pipeline_architecture(outdir)

    _require_nonempty(df, "generate_all_figures")
    figs["fig_2"] = plot_corpus_by_annex_area(df, outdir)
    figs["fig_3"] = plot_context_severity_by_annex_area(df, outdir)
    figs["fig_4"] = plot_dimension_heatmap(df, outdir)
    figs["fig_5"] = plot_evidence_confidence_matrix(df, outdir)
    figs["fig_6"] = plot_sensitivity_comparison(df, outdir)
    return figs

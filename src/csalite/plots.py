"""
Figure generation for CSA-lite manuscript.

Produces 8 figures, each saved in both PNG and SVG formats.
Uses matplotlib ONLY — no seaborn.

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


def fig_1_pipeline_architecture(outdir: Path) -> plt.Figure:
    """
    Fig 1: CSA-lite pipeline architecture diagram (text boxes + arrows).
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

    # Disclaimer note
    ax.text(
        5, -0.3,
        "CSA-lite does not produce legal classifications or compliance determinations.",
        ha="center", va="center", fontsize=7, color="#666", style="italic",
    )
    ax.set_title("CSA-Lite: Analysis Pipeline Architecture", fontsize=12, fontweight="bold", pad=10)

    _save_figure(fig, outdir, "fig_1_pipeline_architecture")
    plt.close(fig)
    return fig


# ── Figure 2 ──────────────────────────────────────────────────────────────────


def fig_2_corpus_by_annex_area(df: pd.DataFrame, outdir: Path) -> plt.Figure:
    """
    Fig 2: Bar chart of case counts by Annex III area.
    """
    _require_nonempty(df, "fig_2_corpus_by_annex_area")

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
    ax.set_title("Fig 2: Corpus Composition by Annex III Area", fontsize=12, fontweight="bold")

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


def fig_3_context_severity_by_annex_area(df: pd.DataFrame, outdir: Path) -> plt.Figure:
    """
    Fig 3: Boxplot with jitter of CSI by Annex III area.
    """
    _require_nonempty(df, "fig_3_context_severity_by_annex_area")
    if "context_severity_index" not in df.columns:
        raise ValueError("context_severity_index column required for fig_3")

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
        "Fig 3: CSI Distribution by Annex III Area\n"
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


def fig_4_dimension_heatmap(df: pd.DataFrame, outdir: Path) -> plt.Figure:
    """
    Fig 4: Heatmap of dimension scores (rows=cases, cols=dimensions).
    Values: 0=green, 1=amber, 2=red, missing=grey.
    """
    _require_nonempty(df, "fig_4_dimension_heatmap")

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

    # Map 0->0, 1->0.5, 2->1.0, nan->-0.1 for colour mapping
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
        "Fig 4: Dimension Score Heatmap (grey = missing)",
        fontsize=11, fontweight="bold",
    )
    fig.tight_layout()

    _save_figure(fig, outdir, "fig_4_dimension_heatmap")
    plt.close(fig)
    return fig


# ── Figure 5 ──────────────────────────────────────────────────────────────────


def fig_5_missingness_matrix(df: pd.DataFrame, outdir: Path) -> plt.Figure:
    """
    Fig 5: Confidence/missingness matrix (rows=cases, cols=dimensions).
    """
    _require_nonempty(df, "fig_5_missingness_matrix")

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
    cbar.set_ticklabels(["missing", "unknown", "low", "medium", "high"])
    cbar.set_label("Evidence Confidence", fontsize=8)

    ax.set_title("Fig 5: Evidence Confidence / Missingness Matrix", fontsize=11, fontweight="bold")
    fig.tight_layout()

    _save_figure(fig, outdir, "fig_5_missingness_matrix")
    plt.close(fig)
    return fig


# ── Figure 6 ──────────────────────────────────────────────────────────────────


def fig_6_sensitivity_band_changes(df: pd.DataFrame, outdir: Path) -> plt.Figure:
    """
    Fig 6: Grouped bar chart of band counts under 3 sensitivity assumptions.
    """
    _require_nonempty(df, "fig_6_sensitivity_band_changes")
    required = {"unknown_as_zero_band", "unknown_as_neutral_band", "unknown_as_conservative_band"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing columns for fig_6: {required - set(df.columns)}")

    areas = sorted(df["annex_iii_area"].dropna().unique())
    n_areas = len(areas)

    assumptions = ["unknown_as_zero_band", "unknown_as_neutral_band", "unknown_as_conservative_band"]
    labels = ["Null=0 (optimistic)", "Null=1 (neutral)", "Null=2 (conservative)"]
    colours = ["#4CAF50", "#FFC107", "#F44336"]

    width = 0.25
    x = np.arange(n_areas)

    fig, ax = plt.subplots(figsize=(max(8, n_areas * 1.5), 6))

    for offset, (col, label, colour) in enumerate(zip(assumptions, labels, colours)):
        counts_high_severe = []
        for area in areas:
            group = df[df["annex_iii_area"] == area]
            n = int(((group[col] == "high") | (group[col] == "severe")).sum())
            counts_high_severe.append(n)
        ax.bar(
            x + (offset - 1) * width,
            counts_high_severe,
            width=width,
            label=label,
            color=colour,
            edgecolor="#333",
            linewidth=0.6,
        )

    ax.set_xticks(x)
    ax.set_xticklabels([a.replace("_", "\n") for a in areas], fontsize=8)
    ax.set_xlabel("EU AI Act Annex III Area", fontsize=10)
    ax.set_ylabel("Cases classified High or Severe", fontsize=10)
    ax.set_title(
        "Fig 6: Sensitivity Analysis — Band Counts by Imputation Assumption\n"
        "(High + Severe cases per assumption)",
        fontsize=11, fontweight="bold",
    )
    ax.legend(fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    _save_figure(fig, outdir, "fig_6_sensitivity_band_changes")
    plt.close(fig)
    return fig


# ── Figure 7 ──────────────────────────────────────────────────────────────────


def fig_7_source_quality_distribution(df: pd.DataFrame, outdir: Path) -> plt.Figure:
    """
    Fig 7: Bar chart of source quality score distribution (0–4).
    """
    _require_nonempty(df, "fig_7_source_quality_distribution")

    scores = pd.to_numeric(df.get("source_quality_score", pd.Series(dtype=float)), errors="coerce").dropna()
    counts = scores.value_counts().sort_index().reindex([0, 1, 2, 3, 4], fill_value=0)

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(
        counts.index,
        counts.values,
        color=["#F44336", "#FF7043", "#FFA726", "#66BB6A", "#2E7D32"],
        edgecolor="#333",
        linewidth=0.8,
    )
    for bar, val in zip(bars, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            str(int(val)),
            ha="center", va="bottom", fontsize=10,
        )
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_xlabel("Source Quality Score (0=very low, 4=very high)", fontsize=10)
    ax.set_ylabel("Number of cases", fontsize=10)
    ax.set_title("Fig 7: Source Quality Score Distribution", fontsize=12, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    _save_figure(fig, outdir, "fig_7_source_quality_distribution")
    plt.close(fig)
    return fig


# ── Figure 8 ──────────────────────────────────────────────────────────────────


def fig_8_dimension_mean_scores(df: pd.DataFrame, outdir: Path) -> plt.Figure:
    """
    Fig 8: Bar chart of mean score per dimension.
    """
    _require_nonempty(df, "fig_8_dimension_mean_scores")

    means = []
    for dim in SCORE_DIMENSIONS:
        col = f"{dim}_score"
        scores = pd.to_numeric(df.get(col, pd.Series(dtype=float)), errors="coerce")
        means.append(round(float(scores.dropna().mean()), 4) if not scores.dropna().empty else 0.0)

    fig, ax = plt.subplots(figsize=(10, 5))
    colours = ["#42A5F5"] * len(SCORE_DIMENSIONS)
    bars = ax.bar(range(len(SCORE_DIMENSIONS)), means, color=colours, edgecolor="#1565C0", linewidth=0.8)

    for bar, val in zip(bars, means):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{val:.2f}",
            ha="center", va="bottom", fontsize=9,
        )

    ax.set_xticks(range(len(SCORE_DIMENSIONS)))
    ax.set_xticklabels(
        [d.replace("_", "\n") for d in SCORE_DIMENSIONS],
        fontsize=8,
    )
    ax.set_ylim(0, 2.3)
    ax.axhline(1.0, color="#888", linestyle="--", linewidth=1, alpha=0.7, label="Mid-point (1.0)")
    ax.set_xlabel("Scoring Dimension", fontsize=10)
    ax.set_ylabel("Mean Score (0–2)", fontsize=10)
    ax.set_title(
        "Fig 8: Mean Dimension Scores Across All Cases",
        fontsize=12, fontweight="bold",
    )
    ax.legend(fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    _save_figure(fig, outdir, "fig_8_dimension_mean_scores")
    plt.close(fig)
    return fig


# ── All figures ────────────────────────────────────────────────────────────────


def generate_all_figures(df: pd.DataFrame, outdir: Path) -> dict[str, plt.Figure]:
    """
    Generate all 8 figures. Fig 1 has no data dependency.

    Raises ValueError if df is empty (for figs 2-8).
    Returns dict of figure name -> Figure.
    """
    figs: dict[str, plt.Figure] = {}
    figs["fig_1"] = fig_1_pipeline_architecture(outdir)

    _require_nonempty(df, "generate_all_figures")
    figs["fig_2"] = fig_2_corpus_by_annex_area(df, outdir)
    figs["fig_3"] = fig_3_context_severity_by_annex_area(df, outdir)
    figs["fig_4"] = fig_4_dimension_heatmap(df, outdir)
    figs["fig_5"] = fig_5_missingness_matrix(df, outdir)
    figs["fig_6"] = fig_6_sensitivity_band_changes(df, outdir)
    figs["fig_7"] = fig_7_source_quality_distribution(df, outdir)
    figs["fig_8"] = fig_8_dimension_mean_scores(df, outdir)
    return figs

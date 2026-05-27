"""
Global constants for CSA-lite.

All constants are immutable. No network calls. No side effects.
"""

from __future__ import annotations

import datetime
from typing import Final

# ── Project identity ──────────────────────────────────────────────────────────
PROJECT_NAME: Final[str] = "CSA-Lite"
PROJECT_VERSION: Final[str] = "0.2.1"
PAPER_TITLE: Final[str] = (
    "Context-Sliced AI Assurance Lite: A Reproducible Public-Records Framework "
    "for Deployment-Conditioned Risk Analysis of AI Systems"
)

# ── Case ID ───────────────────────────────────────────────────────────────────
CASE_ID_PREFIX: Final[str] = "CSA-LITE-"
CASE_ID_PATTERN: Final[str] = r"^CSA-LITE-\d{4}$"

# ── Temporal bounds ───────────────────────────────────────────────────────────
MIN_YEAR: Final[int] = 1950
CURRENT_YEAR: Final[int] = datetime.date.today().year

# ── Scoring dimensions ────────────────────────────────────────────────────────
SCORE_DIMENSIONS: Final[tuple[str, ...]] = (
    "decision_criticality",
    "autonomy",
    "vulnerability",
    "oversight",
    "recourse",
    "scale",
    "opacity",
    "monitoring",
)

SCORE_MIN: Final[int] = 0
SCORE_MAX: Final[int] = 2
SCORE_VALUES: Final[tuple[int | None, ...]] = (0, 1, 2, None)

# ── Severity bands ────────────────────────────────────────────────────────────
SEVERITY_BAND_LOW_MAX: Final[int] = 3
SEVERITY_BAND_MODERATE_MAX: Final[int] = 7
SEVERITY_BAND_HIGH_MAX: Final[int] = 11
SEVERITY_BAND_SEVERE_MAX: Final[int] = 16

# Thresholds: [0,3] low, [4,7] moderate, [8,11] high, [12,16] severe
SEVERITY_THRESHOLDS: Final[dict[str, tuple[int, int]]] = {
    "low": (0, 3),
    "moderate": (4, 7),
    "high": (8, 11),
    "severe": (12, 16),
}

# Maximum possible score = 8 dimensions * 2 = 16
MAX_TOTAL_SCORE: Final[int] = 16

# ── Evidence completeness ─────────────────────────────────────────────────────
CONFIDENCE_WEIGHTS: Final[dict[str, float]] = {
    "high": 1.0,
    "medium": 0.66,
    "low": 0.33,
    "unknown": 0.0,
}

# ── Review flags ──────────────────────────────────────────────────────────────
HIGH_MISSINGNESS_THRESHOLD: Final[int] = 3
LOW_SOURCE_QUALITY_THRESHOLD: Final[int] = 2
LOW_ECI_THRESHOLD: Final[float] = 0.5

# ── Source quality ────────────────────────────────────────────────────────────
SOURCE_QUALITY_MIN: Final[int] = 0
SOURCE_QUALITY_MAX: Final[int] = 4

# ── Text limits ───────────────────────────────────────────────────────────────
MAX_EXCERPT_WORDS: Final[int] = 500

# ── File / path constants ─────────────────────────────────────────────────────
DEFAULT_ENCODING: Final[str] = "utf-8"
CSV_DATE_FORMAT: Final[str] = "%Y-%m-%d"

# ── Reproducibility ───────────────────────────────────────────────────────────
RANDOM_SEED: Final[int] = 42

# ── Figure output ─────────────────────────────────────────────────────────────
FIGURE_DPI: Final[int] = 300
FIGURE_FORMATS: Final[tuple[str, ...]] = ("png", "svg")

# ── Dataset version ───────────────────────────────────────────────────────────
# Dataset version is fixed at 0.2.0 (the 45-case corpus).
# The package/release version (PROJECT_VERSION) may advance without changing the dataset.
DATASET_VERSION: Final[str] = "0.2.0"

# ── Dimension descriptions (for Table 1) ──────────────────────────────────────
DIMENSION_DESCRIPTIONS: Final[dict[str, dict[str, str]]] = {
    "decision_criticality": {
        "description": "Magnitude and reversibility of decisions made by or with the system",
        "score_0": "Advisory / low consequence",
        "score_1": "Consequential but reversible",
        "score_2": "Life- or livelihood-altering",
        "evidence_required": "System output + institutional process",
        "missingness_note": "Code as unknown if outcome chain unclear",
    },
    "autonomy": {
        "description": "Degree to which the system, in practice, determines outcomes",
        "score_0": "Weak advisory; human decides independently",
        "score_1": "Materially influences human decision",
        "score_2": "Automated / de facto determinative",
        "evidence_required": "Human-AI interface + override practice",
        "missingness_note": "Code unknown if practice undocumented",
    },
    "vulnerability": {
        "description": "Structural vulnerability of those subject to system decisions",
        "score_0": "General adult population",
        "score_1": "Asymmetric institutional role (workers, claimants, applicants)",
        "score_2": "Minors / highly dependent groups (detainees, asylum seekers, patients)",
        "evidence_required": "Documentation of affected population",
        "missingness_note": "Code unknown if population unclear",
    },
    "oversight": {
        "description": "Documented quality of human oversight at the point of decision",
        "score_0": "Documented meaningful review with authority to override",
        "score_1": "Nominal / unclear / inconsistent review",
        "score_2": "No meaningful oversight or review only after harm",
        "evidence_required": "Oversight protocols and audit records",
        "missingness_note": "Frequently missing in public records",
    },
    "recourse": {
        "description": "Accessibility and effectiveness of appeal or correction",
        "score_0": "Clear, accessible, timely pathway",
        "score_1": "Partial / slow / costly / inconsistent recourse",
        "score_2": "No meaningful recourse or practically unavailable",
        "evidence_required": "Documented appeal mechanism",
        "missingness_note": "Frequently missing in public records",
    },
    "scale": {
        "description": "Breadth of deployment",
        "score_0": "Pilot / limited internal use",
        "score_1": "Institutional / municipal / regional / sectoral",
        "score_2": "National / platform-scale / high-volume",
        "evidence_required": "Procurement records, deployment scope",
        "missingness_note": "Often inferable from public documents",
    },
    "opacity": {
        "description": "Degree to which system role and decision basis are unavailable",
        "score_0": "Sufficient public documentation",
        "score_1": "Partial opacity with key details missing",
        "score_2": "Proprietary / secret / meaningfully unchallengeable",
        "evidence_required": "Documentation quality and disclosure",
        "missingness_note": "Inferable from disclosure patterns",
    },
    "monitoring": {
        "description": "Presence and quality of post-deployment monitoring",
        "score_0": "Documented systematic audit, monitoring, or evaluation",
        "score_1": "Unclear or periodic monitoring",
        "score_2": "No documented monitoring; failures discovered externally",
        "evidence_required": "Audit reports or external findings",
        "missingness_note": "Frequently missing in public records",
    },
}

# ── Disclaimer (canonical) ────────────────────────────────────────────────────
DISCLAIMER: Final[str] = (
    "CSA-lite does not produce legal classifications, compliance determinations, "
    "conformity assessments, or validated harm predictions. EU AI Act Annex III "
    "categories are used only as an analytical reference frame for grouping "
    "documented deployments by use area. The Context Severity Index is a "
    "transparent structured-coding output derived from public-record evidence. "
    "It is not a legal risk class. Public records may be incomplete, biased, "
    "contested, or outdated."
)

"""
Pydantic v2 data models for CSA-lite cases and scoring outputs.

These models define the canonical data shape for:
  - CSALiteCase: the raw/processed case record
  - ScoredCase: case record enriched with computed scoring fields
  - SourceRecord: entry in the sources manifest

IMPORTANT: These models do NOT produce legal classifications. The Context
Severity Index is a structured-coding output, not a legal risk class.
"""

from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from csalite.constants import (
    CASE_ID_PATTERN,
    CURRENT_YEAR,
    MAX_EXCERPT_WORDS,
    MIN_YEAR,
    SOURCE_QUALITY_MAX,
    SOURCE_QUALITY_MIN,
)
from csalite.enums import (
    AnnexIIIArea,
    AnnexMappingConfidence,
    AnnexMappingType,
    ConfidenceLevel,
    DeployerType,
    DeploymentStatus,
    JurisdictionType,
    SeverityBand,
    SystemType,
)


def _validate_score(v: object) -> int | None:
    """Accept integer 0/1/2 or None; reject anything else."""
    if v is None or (isinstance(v, float) and str(v) == "nan"):
        return None
    if isinstance(v, str) and v.strip() in ("", "nan", "NA", "N/A"):
        return None
    try:
        iv = int(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ValueError(f"Score must be 0, 1, 2, or null; got {v!r}")
    if iv not in (0, 1, 2):
        raise ValueError(f"Score must be 0, 1, or 2; got {iv}")
    return iv


def _validate_confidence(v: object) -> ConfidenceLevel:
    if isinstance(v, ConfidenceLevel):
        return v
    if isinstance(v, str) and v.strip():
        return ConfidenceLevel(v.strip().lower())
    return ConfidenceLevel.unknown


# ── Identification block ──────────────────────────────────────────────────────


class IdentificationFields(BaseModel):
    case_id: str = Field(..., description="Unique case identifier, format CSA-LITE-NNNN")
    case_name: str = Field(..., min_length=1)
    short_label: str = Field(..., min_length=1)
    year_first_reported: int
    year_deployed_or_used: Optional[int] = None
    country: str = Field(..., min_length=1)
    region: str = Field(..., min_length=1)
    jurisdiction_type: JurisdictionType
    source_repository: str = Field(..., min_length=1)
    primary_sources: str = Field(..., min_length=1, description="Semicolon-separated")
    secondary_sources: Optional[str] = None
    source_quality_score: int = Field(..., ge=SOURCE_QUALITY_MIN, le=SOURCE_QUALITY_MAX)
    source_quality_rationale: str = Field(..., min_length=1)

    @field_validator("case_id")
    @classmethod
    def validate_case_id(cls, v: str) -> str:
        if not re.match(CASE_ID_PATTERN, v):
            raise ValueError(f"case_id must match {CASE_ID_PATTERN}; got {v!r}")
        return v

    @field_validator("year_first_reported")
    @classmethod
    def validate_year_reported(cls, v: int) -> int:
        if not (MIN_YEAR <= v <= CURRENT_YEAR):
            raise ValueError(f"year_first_reported must be {MIN_YEAR}–{CURRENT_YEAR}; got {v}")
        return v

    @field_validator("year_deployed_or_used")
    @classmethod
    def validate_year_deployed(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v > CURRENT_YEAR:
            raise ValueError(f"year_deployed_or_used must be <= {CURRENT_YEAR}; got {v}")
        return v


# ── System description block ───────────────────────────────────────────────────


class SystemDescriptionFields(BaseModel):
    system_type: SystemType
    model_or_algorithm_type: Optional[str] = None
    deployer: str = Field(default="unknown", min_length=1)
    deployer_type: DeployerType
    vendor: Optional[str] = None
    public_private_partnership: Optional[bool] = None
    deployment_status: DeploymentStatus
    affected_population: str = Field(..., min_length=1)
    estimated_scale: Optional[str] = None
    scale_basis: Optional[str] = None


# ── Annex III mapping block ────────────────────────────────────────────────────


class AnnexMappingFields(BaseModel):
    annex_iii_area: AnnexIIIArea
    annex_iii_subcategory: Optional[str] = None
    annex_mapping_type: AnnexMappingType
    annex_mapping_confidence: AnnexMappingConfidence
    annex_mapping_rationale: str = Field(..., min_length=1)
    eu_scope_note: Optional[str] = None

    @model_validator(mode="after")
    def check_mapping_consistency(self) -> "AnnexMappingFields":
        if (
            self.annex_mapping_type == AnnexMappingType.direct
            and self.annex_iii_area == AnnexIIIArea.non_annex_comparator
        ):
            raise ValueError(
                "annex_mapping_type='direct' is incompatible with "
                "annex_iii_area='non_annex_comparator'"
            )
        return self


# ── Scoring dimension block ────────────────────────────────────────────────────


class ScoringDimensionFields(BaseModel):
    # decision_criticality
    decision_criticality_score: Optional[int] = None
    decision_criticality_rationale: str = Field(default="")
    decision_criticality_confidence: ConfidenceLevel = ConfidenceLevel.unknown

    # autonomy
    autonomy_score: Optional[int] = None
    autonomy_rationale: str = Field(default="")
    autonomy_confidence: ConfidenceLevel = ConfidenceLevel.unknown

    # vulnerability
    vulnerability_score: Optional[int] = None
    vulnerability_rationale: str = Field(default="")
    vulnerability_confidence: ConfidenceLevel = ConfidenceLevel.unknown

    # oversight
    oversight_score: Optional[int] = None
    oversight_rationale: str = Field(default="")
    oversight_confidence: ConfidenceLevel = ConfidenceLevel.unknown

    # recourse
    recourse_score: Optional[int] = None
    recourse_rationale: str = Field(default="")
    recourse_confidence: ConfidenceLevel = ConfidenceLevel.unknown

    # scale
    scale_score: Optional[int] = None
    scale_rationale: str = Field(default="")
    scale_confidence: ConfidenceLevel = ConfidenceLevel.unknown

    # opacity
    opacity_score: Optional[int] = None
    opacity_rationale: str = Field(default="")
    opacity_confidence: ConfidenceLevel = ConfidenceLevel.unknown

    # monitoring
    monitoring_score: Optional[int] = None
    monitoring_rationale: str = Field(default="")
    monitoring_confidence: ConfidenceLevel = ConfidenceLevel.unknown

    # ── Score validators ──
    @field_validator(
        "decision_criticality_score",
        "autonomy_score",
        "vulnerability_score",
        "oversight_score",
        "recourse_score",
        "scale_score",
        "opacity_score",
        "monitoring_score",
        mode="before",
    )
    @classmethod
    def validate_score_field(cls, v: object) -> int | None:
        return _validate_score(v)

    # ── Confidence validators ──
    @field_validator(
        "decision_criticality_confidence",
        "autonomy_confidence",
        "vulnerability_confidence",
        "oversight_confidence",
        "recourse_confidence",
        "scale_confidence",
        "opacity_confidence",
        "monitoring_confidence",
        mode="before",
    )
    @classmethod
    def validate_confidence_field(cls, v: object) -> ConfidenceLevel:
        return _validate_confidence(v)

    @model_validator(mode="after")
    def check_score_rationale_pairs(self) -> "ScoringDimensionFields":
        from csalite.constants import SCORE_DIMENSIONS

        for dim in SCORE_DIMENSIONS:
            score = getattr(self, f"{dim}_score")
            rationale = getattr(self, f"{dim}_rationale")
            if score is not None and not rationale.strip():
                raise ValueError(
                    f"Non-null score for '{dim}' requires a non-empty rationale"
                )
        return self


# ── Documentation block ────────────────────────────────────────────────────────


class DocumentationFields(BaseModel):
    public_record_excerpt: Optional[str] = None
    coding_notes: Optional[str] = None
    ambiguity_flags: Optional[str] = None
    exclusion_reason: Optional[str] = None
    last_verified_date: Optional[str] = None  # ISO YYYY-MM-DD

    @field_validator("public_record_excerpt")
    @classmethod
    def validate_excerpt_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            word_count = len(v.split())
            if word_count > MAX_EXCERPT_WORDS:
                raise ValueError(
                    f"public_record_excerpt exceeds {MAX_EXCERPT_WORDS} words "
                    f"(got {word_count})"
                )
        return v

    @field_validator("last_verified_date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            import datetime

            try:
                datetime.date.fromisoformat(v.strip())
            except ValueError:
                raise ValueError(
                    f"last_verified_date must be ISO format YYYY-MM-DD; got {v!r}"
                )
        return v


# ── Composite case model ───────────────────────────────────────────────────────


class CSALiteCase(
    IdentificationFields,
    SystemDescriptionFields,
    AnnexMappingFields,
    ScoringDimensionFields,
    DocumentationFields,
):
    """
    Canonical CSA-lite case record combining all field groups.

    Inherits validation from all parent field blocks via Pydantic v2
    multiple-inheritance composition.
    """

    model_config = {"str_strip_whitespace": True, "validate_default": True}


# ── Scored case model ──────────────────────────────────────────────────────────


class ScoredCase(CSALiteCase):
    """
    CSA-lite case enriched with computed scoring and review flag fields.

    All computed fields are added by scoring.py and are read-only
    after construction.
    """

    context_severity_index: Optional[int] = None
    context_severity_band: SeverityBand = SeverityBand.unknown
    known_dimension_count: int = 0
    missing_dimensions_count: int = 0
    evidence_completeness_index: float = 0.0

    unknown_as_zero_score: Optional[int] = None
    unknown_as_neutral_score: Optional[int] = None
    unknown_as_conservative_score: Optional[int] = None
    unknown_as_zero_band: SeverityBand = SeverityBand.unknown
    unknown_as_neutral_band: SeverityBand = SeverityBand.unknown
    unknown_as_conservative_band: SeverityBand = SeverityBand.unknown

    sensitivity_band_change: bool = False
    high_missingness_flag: bool = False
    low_source_quality_flag: bool = False
    review_required_flag: bool = False


# ── Source record model ────────────────────────────────────────────────────────


class SourceRecord(BaseModel):
    """Entry in the sources manifest (sources_manifest.csv)."""

    source_id: str = Field(..., min_length=1)
    case_id: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    source_type: str = Field(
        ...,
        description=(
            "Type of source: e.g., news_article, government_report, court_ruling, "
            "academic_paper, ngo_report, audit_report, freedom_of_information, other"
        ),
    )
    access_date: Optional[str] = None  # ISO YYYY-MM-DD
    archive_url: Optional[str] = None
    language: str = Field(default="en")
    quality_contribution: Optional[str] = None

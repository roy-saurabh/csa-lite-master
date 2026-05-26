"""
Validation engine for CSA-lite case data.

Implements all 18 validation rules specified in the coding protocol.
Returns structured ValidationResult objects — no side effects, no network calls.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import pandas as pd

from csalite.constants import (
    CASE_ID_PATTERN,
    CURRENT_YEAR,
    MAX_EXCERPT_WORDS,
    MIN_YEAR,
    SCORE_DIMENSIONS,
    SOURCE_QUALITY_MAX,
    SOURCE_QUALITY_MIN,
)
from csalite.enums import (
    AnnexIIIArea,
    AnnexMappingType,
    ConfidenceLevel,
    DeploymentStatus,
)


class Severity(str, Enum):
    error = "error"
    warning = "warning"
    info = "info"


@dataclass
class ValidationIssue:
    severity: Severity
    rule_id: str
    field: str
    case_id: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] rule={self.rule_id} field={self.field} case={self.case_id}: {self.message}"


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.error]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.warning]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, rule_id: str, field: str, case_id: str, message: str) -> None:
        self.issues.append(
            ValidationIssue(Severity.error, rule_id, field, case_id, message)
        )

    def add_warning(self, rule_id: str, field: str, case_id: str, message: str) -> None:
        self.issues.append(
            ValidationIssue(Severity.warning, rule_id, field, case_id, message)
        )

    def add_info(self, rule_id: str, field: str, case_id: str, message: str) -> None:
        self.issues.append(
            ValidationIssue(Severity.info, rule_id, field, case_id, message)
        )

    def summary(self) -> str:
        n_err = len(self.errors)
        n_warn = len(self.warnings)
        status = "PASS" if self.is_valid else "FAIL"
        return f"{status}: {n_err} error(s), {n_warn} warning(s)"


# ── Helpers ───────────────────────────────────────────────────────────────────


def _is_missing(val: Any) -> bool:
    """True if val is None, NaN, or empty string."""
    if val is None:
        return True
    if isinstance(val, float):
        import math

        return math.isnan(val)
    if isinstance(val, str):
        return val.strip() == ""
    return False


def _coerce_score(val: Any) -> int | None:
    if _is_missing(val):
        return None
    try:
        iv = int(val)
        if iv in (0, 1, 2):
            return iv
    except (TypeError, ValueError):
        pass
    return None


def _str_val(row: pd.Series, col: str) -> str:
    v = row.get(col, "")
    if _is_missing(v):
        return ""
    return str(v).strip()


def _int_val(row: pd.Series, col: str) -> int | None:
    v = row.get(col)
    if _is_missing(v):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


# ── Rule implementations ──────────────────────────────────────────────────────


REQUIRED_FIELDS = [
    "case_id",
    "case_name",
    "short_label",
    "year_first_reported",
    "country",
    "region",
    "jurisdiction_type",
    "source_repository",
    "primary_sources",
    "source_quality_score",
    "source_quality_rationale",
    "system_type",
    "deployer",
    "deployer_type",
    "deployment_status",
    "affected_population",
    "annex_iii_area",
    "annex_mapping_type",
    "annex_mapping_confidence",
    "annex_mapping_rationale",
]

_VALID_CONFIDENCES = {c.value for c in ConfidenceLevel}
_STATUSES_REQUIRING_NOTES = {
    DeploymentStatus.withdrawn.value,
    DeploymentStatus.suspended.value,
    DeploymentStatus.litigated.value,
}


def _rule_01_required_fields(row: pd.Series, result: ValidationResult) -> None:
    """Rule 01: All required fields present."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    for f in REQUIRED_FIELDS:
        if _is_missing(row.get(f)):
            result.add_error("R01", f, case_id, f"Required field '{f}' is missing or empty")


def _rule_02_case_id(row: pd.Series, result: ValidationResult, seen_ids: set[str]) -> None:
    """Rule 02: case_id unique + matches pattern."""
    case_id = _str_val(row, "case_id")
    if not case_id:
        return  # already caught by R01
    if not re.match(CASE_ID_PATTERN, case_id):
        result.add_error(
            "R02", "case_id", case_id, f"case_id must match {CASE_ID_PATTERN}"
        )
    if case_id in seen_ids:
        result.add_error("R02", "case_id", case_id, "Duplicate case_id")
    seen_ids.add(case_id)


def _rule_03_scores(row: pd.Series, result: ValidationResult) -> None:
    """Rule 03: Scores must be 0, 1, 2, or null."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    for dim in SCORE_DIMENSIONS:
        col = f"{dim}_score"
        val = row.get(col)
        if _is_missing(val):
            continue
        try:
            iv = int(val)
        except (TypeError, ValueError):
            result.add_error("R03", col, case_id, f"Score value {val!r} is not an integer")
            continue
        if iv not in (0, 1, 2):
            result.add_error("R03", col, case_id, f"Score must be 0, 1, or 2; got {iv}")


def _rule_04_confidence_enums(row: pd.Series, result: ValidationResult) -> None:
    """Rule 04: Confidence fields must be valid enum values."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    for dim in SCORE_DIMENSIONS:
        col = f"{dim}_confidence"
        val = _str_val(row, col)
        if val and val not in _VALID_CONFIDENCES:
            result.add_error(
                "R04", col, case_id,
                f"Confidence value {val!r} not in {sorted(_VALID_CONFIDENCES)}"
            )


def _rule_05_source_quality_score(row: pd.Series, result: ValidationResult) -> None:
    """Rule 05: source_quality_score must be 0-4."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    val = row.get("source_quality_score")
    if _is_missing(val):
        return
    try:
        iv = int(val)
    except (TypeError, ValueError):
        result.add_error("R05", "source_quality_score", case_id, f"Not an integer: {val!r}")
        return
    if not (SOURCE_QUALITY_MIN <= iv <= SOURCE_QUALITY_MAX):
        result.add_error(
            "R05", "source_quality_score", case_id,
            f"source_quality_score must be {SOURCE_QUALITY_MIN}-{SOURCE_QUALITY_MAX}; got {iv}"
        )


def _rule_06_score_rationale_required(row: pd.Series, result: ValidationResult) -> None:
    """Rule 06: Non-null score must have non-empty rationale."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    for dim in SCORE_DIMENSIONS:
        score_val = row.get(f"{dim}_score")
        if _is_missing(score_val):
            continue
        try:
            iv = int(score_val)
        except (TypeError, ValueError):
            continue
        if iv in (0, 1, 2):
            rationale = _str_val(row, f"{dim}_rationale")
            if not rationale:
                result.add_error(
                    "R06", f"{dim}_rationale", case_id,
                    f"Non-null score for '{dim}' requires a non-empty rationale"
                )


def _rule_07_null_score_note(row: pd.Series, result: ValidationResult) -> None:
    """Rule 07: Null score should have rationale or ambiguity_flag."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    ambiguity = _str_val(row, "ambiguity_flags")
    for dim in SCORE_DIMENSIONS:
        if _is_missing(row.get(f"{dim}_score")):
            rationale = _str_val(row, f"{dim}_rationale")
            if not rationale and not ambiguity:
                result.add_warning(
                    "R07", f"{dim}_rationale", case_id,
                    f"Null score for '{dim}' has no rationale or ambiguity_flag"
                )


def _rule_08_at_least_one_source(row: pd.Series, result: ValidationResult) -> None:
    """Rule 08: At least one primary source must be specified."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    sources = _str_val(row, "primary_sources")
    if not sources:
        result.add_error(
            "R08", "primary_sources", case_id,
            "At least one primary source is required"
        )


def _rule_09_annex_rationale(row: pd.Series, result: ValidationResult) -> None:
    """Rule 09: Annex III mapping must have rationale."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    rationale = _str_val(row, "annex_mapping_rationale")
    if not rationale:
        result.add_error(
            "R09", "annex_mapping_rationale", case_id,
            "annex_mapping_rationale is required for all cases"
        )


def _rule_10_low_known_dimensions(row: pd.Series, result: ValidationResult) -> None:
    """Rule 10: Fewer than 5 known dimensions -> informational flag."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    known = sum(1 for dim in SCORE_DIMENSIONS if not _is_missing(row.get(f"{dim}_score")))
    if known < 5:
        result.add_info(
            "R10", "scores", case_id,
            f"Only {known}/8 dimensions have scores; high missingness may limit comparability"
        )


def _rule_11_direct_non_annex_conflict(row: pd.Series, result: ValidationResult) -> None:
    """Rule 11: annex_mapping_type=direct + annex_iii_area=non_annex_comparator is an error."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    mapping_type = _str_val(row, "annex_mapping_type")
    area = _str_val(row, "annex_iii_area")
    if (
        mapping_type == AnnexMappingType.direct.value
        and area == AnnexIIIArea.non_annex_comparator.value
    ):
        result.add_error(
            "R11", "annex_mapping_type", case_id,
            "annex_mapping_type='direct' is incompatible with annex_iii_area='non_annex_comparator'"
        )


def _rule_12_comparator_annex_mismatch(row: pd.Series, result: ValidationResult) -> None:
    """Rule 12: annex_mapping_type=comparator + non-non_annex area -> warning unless rationale given."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    mapping_type = _str_val(row, "annex_mapping_type")
    area = _str_val(row, "annex_iii_area")
    rationale = _str_val(row, "annex_mapping_rationale")
    if (
        mapping_type == AnnexMappingType.comparator.value
        and area != AnnexIIIArea.non_annex_comparator.value
        and not rationale
    ):
        result.add_warning(
            "R12", "annex_mapping_type", case_id,
            "annex_mapping_type='comparator' with non-non_annex area and no rationale"
        )


def _rule_13_last_verified_date(row: pd.Series, result: ValidationResult) -> None:
    """Rule 13: last_verified_date must be ISO YYYY-MM-DD."""
    import datetime

    case_id = _str_val(row, "case_id") or "<unknown>"
    val = _str_val(row, "last_verified_date")
    if val:
        try:
            datetime.date.fromisoformat(val)
        except ValueError:
            result.add_error(
                "R13", "last_verified_date", case_id,
                f"last_verified_date must be YYYY-MM-DD; got {val!r}"
            )


def _rule_14_year_reported_bounds(row: pd.Series, result: ValidationResult) -> None:
    """Rule 14: year_first_reported 1950-current_year."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    year = _int_val(row, "year_first_reported")
    if year is not None and not (MIN_YEAR <= year <= CURRENT_YEAR):
        result.add_error(
            "R14", "year_first_reported", case_id,
            f"year_first_reported must be {MIN_YEAR}-{CURRENT_YEAR}; got {year}"
        )


def _rule_15_year_deployed_bounds(row: pd.Series, result: ValidationResult) -> None:
    """Rule 15: year_deployed_or_used null or <= current_year."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    val = row.get("year_deployed_or_used")
    if _is_missing(val):
        return
    try:
        year = int(val)
    except (TypeError, ValueError):
        result.add_error(
            "R15", "year_deployed_or_used", case_id,
            f"year_deployed_or_used must be an integer or null; got {val!r}"
        )
        return
    if year > CURRENT_YEAR:
        result.add_error(
            "R15", "year_deployed_or_used", case_id,
            f"year_deployed_or_used must be <= {CURRENT_YEAR}; got {year}"
        )


def _rule_16_withdrawn_coding_notes(row: pd.Series, result: ValidationResult) -> None:
    """Rule 16: withdrawn/suspended/litigated cases must have coding_notes."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    status = _str_val(row, "deployment_status")
    if status in _STATUSES_REQUIRING_NOTES:
        notes = _str_val(row, "coding_notes")
        if not notes:
            result.add_error(
                "R16", "coding_notes", case_id,
                f"deployment_status='{status}' requires non-empty coding_notes"
            )


def _rule_17_excerpt_word_count(row: pd.Series, result: ValidationResult) -> None:
    """Rule 17: public_record_excerpt <= 500 words."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    excerpt = _str_val(row, "public_record_excerpt")
    if excerpt:
        wc = len(excerpt.split())
        if wc > MAX_EXCERPT_WORDS:
            result.add_error(
                "R17", "public_record_excerpt", case_id,
                f"public_record_excerpt exceeds {MAX_EXCERPT_WORDS} words (got {wc})"
            )


def _rule_18_no_personal_data_fields(row: pd.Series, result: ValidationResult) -> None:
    """Rule 18: No raw personal data fields (structural check on column names)."""
    case_id = _str_val(row, "case_id") or "<unknown>"
    personal_data_indicators = [
        "name", "email", "phone", "address", "dob", "date_of_birth",
        "national_id", "passport", "ssn", "ip_address", "user_id",
    ]
    for col in row.index:
        col_lower = col.lower()
        for indicator in personal_data_indicators:
            if indicator in col_lower and col_lower not in (
                "case_name",
                "short_label",
                "case_id",
                "affected_population",
                "url",
                "primary_sources",
                "secondary_sources",
                "annex_iii_subcategory",
            ):
                result.add_warning(
                    "R18", col, case_id,
                    f"Column '{col}' may contain personal data (matches indicator '{indicator}')"
                )
                break


# ── Public API ────────────────────────────────────────────────────────────────


def validate_dataframe(df: pd.DataFrame) -> ValidationResult:
    """
    Validate a DataFrame of CSA-lite cases.

    Applies all 18 validation rules. Returns a ValidationResult.
    Does not raise — callers should inspect result.is_valid.
    """
    result = ValidationResult()
    seen_ids: set[str] = set()

    for _, row in df.iterrows():
        _rule_01_required_fields(row, result)
        _rule_02_case_id(row, result, seen_ids)
        _rule_03_scores(row, result)
        _rule_04_confidence_enums(row, result)
        _rule_05_source_quality_score(row, result)
        _rule_06_score_rationale_required(row, result)
        _rule_07_null_score_note(row, result)
        _rule_08_at_least_one_source(row, result)
        _rule_09_annex_rationale(row, result)
        _rule_10_low_known_dimensions(row, result)
        _rule_11_direct_non_annex_conflict(row, result)
        _rule_12_comparator_annex_mismatch(row, result)
        _rule_13_last_verified_date(row, result)
        _rule_14_year_reported_bounds(row, result)
        _rule_15_year_deployed_bounds(row, result)
        _rule_16_withdrawn_coding_notes(row, result)
        _rule_17_excerpt_word_count(row, result)
        _rule_18_no_personal_data_fields(row, result)

    return result


def validate_record(record: dict[str, Any]) -> ValidationResult:
    """Validate a single case record (dict)."""
    df = pd.DataFrame([record])
    return validate_dataframe(df)

"""
Tests for JSON schema validation of case and source records.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
SCHEMAS = Path(__file__).parent.parent / "schemas"


@pytest.fixture
def case_schema() -> dict:
    with (SCHEMAS / "case.schema.json").open() as fh:
        return json.load(fh)


@pytest.fixture
def sources_schema() -> dict:
    with (SCHEMAS / "sources.schema.json").open() as fh:
        return json.load(fh)


@pytest.fixture
def valid_cases_df():
    from csalite.io import read_cases_csv
    return read_cases_csv(FIXTURES / "valid_cases_minimal.csv")


@pytest.fixture
def invalid_cases_df():
    from csalite.io import read_cases_csv
    return read_cases_csv(FIXTURES / "invalid_cases_missing_required.csv")


@pytest.fixture
def valid_sources_df():
    from csalite.io import read_sources_csv
    return read_sources_csv(FIXTURES / "valid_sources_manifest.csv")


def test_case_schema_file_exists():
    assert (SCHEMAS / "case.schema.json").exists()


def test_sources_schema_file_exists():
    assert (SCHEMAS / "sources.schema.json").exists()


def test_scoring_schema_file_exists():
    assert (SCHEMAS / "scoring.schema.json").exists()


def test_invalid_case_id_pattern_caught(case_schema):
    bad_record = {
        "case_id": "INVALID-001",  # wrong pattern
        "case_name": "Test Case",
        "short_label": "Test",
        "year_first_reported": 2020,
        "country": "Fixtureland",
        "region": "FixtureRegion",
        "jurisdiction_type": "unknown",
        "source_repository": "fixture",
        "primary_sources": "https://example.com",
        "source_quality_score": 3,
        "source_quality_rationale": "OK",
        "system_type": "scoring_system",
        "deployer": "unknown",
        "deployer_type": "unknown",
        "deployment_status": "deployed",
        "affected_population": "General population",
        "annex_iii_area": "unclear",
        "annex_mapping_type": "unclear",
        "annex_mapping_confidence": "unknown",
        "annex_mapping_rationale": "Rationale here",
    }
    from csalite.io import validate_record_against_schema
    errs = validate_record_against_schema(bad_record, case_schema)
    assert len(errs) > 0
    assert any("case_id" in e or "pattern" in e.lower() for e in errs)


def test_valid_sources_pass_schema(valid_sources_df, sources_schema):
    from csalite.io import validate_dataframe_against_schema
    errors = validate_dataframe_against_schema(valid_sources_df, sources_schema)
    assert errors == {}, f"Schema errors: {errors}"


def test_source_missing_required_field_caught(sources_schema):
    bad_record = {
        "source_id": "SRC-9999",
        # missing case_id, url, title, source_type
    }
    from csalite.io import validate_record_against_schema
    errs = validate_record_against_schema(bad_record, sources_schema)
    assert len(errs) > 0


def test_score_out_of_range_caught(case_schema):
    """Score of 3 should fail schema validation."""
    record = {
        "case_id": "CSA-LITE-0001",
        "case_name": "Test",
        "short_label": "T",
        "year_first_reported": 2020,
        "country": "X",
        "region": "Y",
        "jurisdiction_type": "unknown",
        "source_repository": "r",
        "primary_sources": "https://example.com",
        "source_quality_score": 3,
        "source_quality_rationale": "ok",
        "system_type": "scoring_system",
        "deployer": "unknown",
        "deployer_type": "unknown",
        "deployment_status": "deployed",
        "affected_population": "General population",
        "annex_iii_area": "unclear",
        "annex_mapping_type": "unclear",
        "annex_mapping_confidence": "unknown",
        "annex_mapping_rationale": "Rationale",
        "decision_criticality_score": 3,  # invalid
    }
    from csalite.io import validate_record_against_schema
    errs = validate_record_against_schema(record, case_schema)
    assert len(errs) > 0


def test_valid_record_passes_schema(case_schema):
    """A minimal valid record should pass schema validation."""
    record = {
        "case_id": "CSA-LITE-0001",
        "case_name": "Test Case",
        "short_label": "TestCase",
        "year_first_reported": 2020,
        "country": "Fixtureland",
        "region": "FixtureRegion",
        "jurisdiction_type": "unknown",
        "source_repository": "fixture-repo",
        "primary_sources": "https://example.com",
        "source_quality_score": 3,
        "source_quality_rationale": "Three sources",
        "system_type": "scoring_system",
        "deployer": "Fixture Authority",
        "deployer_type": "public_authority",
        "deployment_status": "deployed",
        "affected_population": "General population",
        "annex_iii_area": "unclear",
        "annex_mapping_type": "unclear",
        "annex_mapping_confidence": "unknown",
        "annex_mapping_rationale": "Area unclear from public records",
    }
    from csalite.io import validate_record_against_schema
    errs = validate_record_against_schema(record, case_schema)
    assert errs == [], f"Unexpected errors: {errs}"


def test_validation_rules_on_invalid_fixture(invalid_cases_df):
    """invalid_cases_missing_required.csv should fail validation with errors."""
    from csalite.validation import validate_dataframe
    result = validate_dataframe(invalid_cases_df)
    assert not result.is_valid
    # Should catch missing case_name
    field_names = [issue.field for issue in result.errors]
    assert "case_name" in field_names


def test_validation_passes_for_valid_fixture(valid_cases_df):
    """valid_cases_minimal.csv should pass validation."""
    from csalite.validation import validate_dataframe
    result = validate_dataframe(valid_cases_df)
    assert result.is_valid, f"Unexpected errors: {[str(e) for e in result.errors]}"

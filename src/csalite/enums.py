"""
Controlled-vocabulary enumerations for CSA-lite.

All enums use string values for CSV/JSON interoperability.
"""

from __future__ import annotations

from enum import Enum


class JurisdictionType(str, Enum):
    eu_member_state = "eu_member_state"
    european_non_eu = "european_non_eu"
    united_kingdom = "united_kingdom"
    united_states = "united_states"
    canada = "canada"
    latin_america = "latin_america"
    africa = "africa"
    middle_east = "middle_east"
    south_asia = "south_asia"
    east_asia = "east_asia"
    southeast_asia = "southeast_asia"
    oceania = "oceania"
    multi_jurisdiction = "multi_jurisdiction"
    unknown = "unknown"


class AnnexIIIArea(str, Enum):
    biometrics = "biometrics"
    critical_infrastructure = "critical_infrastructure"
    education_vocational_training = "education_vocational_training"
    employment_worker_management = "employment_worker_management"
    essential_services_benefits = "essential_services_benefits"
    law_enforcement = "law_enforcement"
    migration_asylum_border_control = "migration_asylum_border_control"
    justice_democratic_processes = "justice_democratic_processes"
    non_annex_comparator = "non_annex_comparator"
    unclear = "unclear"


class AnnexMappingType(str, Enum):
    direct = "direct"
    analogous = "analogous"
    comparator = "comparator"
    unclear = "unclear"


class AnnexMappingConfidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    unknown = "unknown"


class SystemType(str, Enum):
    predictive_model = "predictive_model"
    scoring_system = "scoring_system"
    ranking_system = "ranking_system"
    biometric_identification = "biometric_identification"
    biometric_categorisation = "biometric_categorisation"
    facial_recognition = "facial_recognition"
    risk_assessment = "risk_assessment"
    eligibility_determination = "eligibility_determination"
    fraud_detection = "fraud_detection"
    recommender_or_allocation_system = "recommender_or_allocation_system"
    generative_ai_system = "generative_ai_system"
    automated_decision_system = "automated_decision_system"
    surveillance_or_monitoring_system = "surveillance_or_monitoring_system"
    other = "other"
    unknown = "unknown"


class DeployerType(str, Enum):
    public_authority = "public_authority"
    private_company = "private_company"
    public_private_partnership = "public_private_partnership"
    education_institution = "education_institution"
    healthcare_provider = "healthcare_provider"
    law_enforcement_agency = "law_enforcement_agency"
    court_or_justice_body = "court_or_justice_body"
    employer = "employer"
    platform = "platform"
    border_or_migration_authority = "border_or_migration_authority"
    welfare_or_social_service_agency = "welfare_or_social_service_agency"
    financial_institution = "financial_institution"
    unknown = "unknown"


class DeploymentStatus(str, Enum):
    deployed = "deployed"
    piloted = "piloted"
    procured = "procured"
    planned = "planned"
    withdrawn = "withdrawn"
    suspended = "suspended"
    litigated = "litigated"
    reported_incident = "reported_incident"
    unknown = "unknown"


class ConfidenceLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"
    unknown = "unknown"


class SeverityBand(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    severe = "severe"
    unknown = "unknown"

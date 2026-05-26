# Annex III Mapping Rubric

## Purpose

This rubric guides the mapping of real-world AI system deployments to EU AI Act
Annex III use areas. The mapping is used as an analytical reference frame for
grouping cases — it does NOT constitute a legal compliance determination.

## Important Disclaimer

> Mapping a case to an Annex III area does NOT mean the system is legally
> classified as high-risk under the EU AI Act. The EU AI Act's legal scope
> depends on factors not assessed here (e.g., deployer jurisdiction, system
> provider status, intended purpose as legally defined, prohibited system checks,
> exemptions). CSA-lite uses Annex III areas only as an internationally
> recognised typology for categorising AI deployments by use domain.

## Mapping Types

| Type | Meaning | When to use |
|------|---------|-------------|
| `direct` | The system's documented use matches an Annex III area description closely | Use area is clear and unambiguous |
| `analogous` | The system's use is similar to but not identical to an Annex III area | Some definitional ambiguity; reasonable mapping |
| `comparator` | The system operates outside EU AI Act scope but is mapped for cross-domain comparison | Always used with `non_annex_comparator` for the area |
| `unclear` | Insufficient evidence to determine the appropriate mapping | Evidence does not permit confident mapping |

## Annex III Areas and Their Use Domains

| Area value | EU AI Act Annex III scope |
|-----------|--------------------------|
| `biometrics` | Remote biometric identification; categorisation of natural persons |
| `critical_infrastructure` | Safety components of critical digital infrastructure |
| `education_vocational_training` | Access to education; evaluation; monitoring during exams |
| `employment_worker_management` | Recruitment; performance monitoring; task allocation |
| `essential_services_benefits` | Credit; insurance; public benefits eligibility; emergency services |
| `law_enforcement` | Risk assessment; polygraphs; crime analytics; predictive policing |
| `migration_asylum_border_control` | Risk assessment; lie detection; border management |
| `justice_democratic_processes` | Judicial fact-finding; AI for elections |
| `non_annex_comparator` | Use area does not fall within Annex III (for comparator cases) |
| `unclear` | Mapping cannot be determined from available evidence |

## Mapping Confidence

| Level | Meaning |
|-------|---------|
| `high` | Clear documentary evidence directly supports the mapping |
| `medium` | Mapping is reasonable but requires interpretation |
| `low` | Significant uncertainty in the mapping |
| `unknown` | Unable to assess confidence from available evidence |

## Rule: Direct + Non-Annex

`annex_mapping_type = direct` CANNOT be combined with `annex_iii_area = non_annex_comparator`.
This combination is a coding error and will be flagged by the validation engine.

## Rationale Requirement

All cases require a non-empty `annex_mapping_rationale`. The rationale must
explain:
1. Why this Annex III area was selected
2. Which documentary evidence supports the mapping
3. Any ambiguities or limitations in the mapping

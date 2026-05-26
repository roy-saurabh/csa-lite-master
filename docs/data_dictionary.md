# Data Dictionary

Complete field-by-field description of all fields in `csa_lite_cases.csv`.

## A. Identification Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `case_id` | string | Yes | Unique identifier matching `^CSA-LITE-\d{4}$` |
| `case_name` | string | Yes | Full descriptive name of the case |
| `short_label` | string | Yes | Short label for figures (max ~20 chars) |
| `year_first_reported` | integer | Yes | Year the case was first documented publicly (1950–current) |
| `year_deployed_or_used` | integer | No | Year the system was first deployed or used |
| `country` | string | Yes | Country of deployment |
| `region` | string | Yes | World region |
| `jurisdiction_type` | enum | Yes | Legal jurisdiction category |
| `source_repository` | string | Yes | Name of primary source database/archive |
| `primary_sources` | string | Yes | Semicolon-separated URLs/DOIs of primary sources |
| `secondary_sources` | string | No | Semicolon-separated URLs/DOIs of secondary sources |
| `source_quality_score` | integer (0–4) | Yes | Overall source quality rating |
| `source_quality_rationale` | string | Yes | Justification for the source quality score |

## B. System Description Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `system_type` | enum | Yes | Type of AI system |
| `model_or_algorithm_type` | string | No | Specific algorithm or model type (e.g., "logistic regression") |
| `deployer` | string | Yes | Name of deploying organisation (default: "unknown") |
| `deployer_type` | enum | Yes | Category of deployer |
| `vendor` | string | No | Name of vendor/supplier if distinct from deployer |
| `public_private_partnership` | boolean | No | Whether deployment is a PPP |
| `deployment_status` | enum | Yes | Current deployment status |
| `affected_population` | string | Yes | Description of population affected |
| `estimated_scale` | string | No | Estimated scale (e.g., "800,000 individuals/year") |
| `scale_basis` | string | No | Evidence basis for the scale estimate |

## C. Annex III Mapping Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `annex_iii_area` | enum | Yes | EU AI Act Annex III area (analytical reference only) |
| `annex_iii_subcategory` | string | No | More specific subcategory |
| `annex_mapping_type` | enum | Yes | direct / analogous / comparator / unclear |
| `annex_mapping_confidence` | enum | Yes | Confidence in the mapping |
| `annex_mapping_rationale` | string | Yes | Explanation of the mapping decision |
| `eu_scope_note` | string | No | Note on EU AI Act jurisdictional scope |

## D. Scoring Dimension Fields

For each of 8 dimensions (decision_criticality, autonomy, vulnerability,
oversight, recourse, scale, opacity, monitoring):

| Field pattern | Type | Description |
|---------------|------|-------------|
| `{dim}_score` | integer (0/1/2) or null | Coded score; null = evidence insufficient |
| `{dim}_rationale` | string | Required for non-null scores; recommended for null |
| `{dim}_confidence` | enum (high/medium/low/unknown) | Evidence confidence for this score |

## E. Documentation Fields

| Field | Type | Description |
|-------|------|-------------|
| `public_record_excerpt` | string (≤500 words) | Direct excerpt or paraphrase from primary source |
| `coding_notes` | string | Coder's notes; required for withdrawn/suspended/litigated |
| `ambiguity_flags` | string | Unresolved ambiguities |
| `exclusion_reason` | string | Why an included-with-caveats case was not excluded |
| `last_verified_date` | ISO date (YYYY-MM-DD) | Date record was last checked against sources |

## Computed Fields (scored_cases.csv only)

| Field | Type | Description |
|-------|------|-------------|
| `context_severity_index` | integer (0–16) | CSI under neutral (null=1) imputation |
| `context_severity_band` | enum | Severity band: low/moderate/high/severe/unknown |
| `known_dimension_count` | integer (0–8) | Number of non-null scores |
| `missing_dimensions_count` | integer (0–8) | Number of null scores |
| `evidence_completeness_index` | float (0–1) | Weighted mean confidence |
| `unknown_as_zero_score` | integer | CSI with null=0 |
| `unknown_as_neutral_score` | integer | CSI with null=1 |
| `unknown_as_conservative_score` | integer | CSI with null=2 |
| `unknown_as_{assumption}_band` | enum | Severity band for each assumption |
| `sensitivity_band_change` | boolean | True if bands differ across assumptions |
| `high_missingness_flag` | boolean | True if missing_dimensions_count >= 3 |
| `low_source_quality_flag` | boolean | True if source_quality_score <= 2 |
| `review_required_flag` | boolean | True if any flag or (high/severe + ECI < 0.5) |

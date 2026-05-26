# CSA-Lite Coding Protocol

## Purpose

This document defines the standardised procedures for identifying, screening,
and coding AI system deployment cases for the CSA-lite dataset. All coders
must follow this protocol to ensure intercoder reliability.

## Step 1: Case Identification

A case is eligible for inclusion if:
1. It concerns an AI system deployed (or formally piloted) in a real-world context
2. Sufficient public-record documentation exists to complete at least 5 of 8 scoring dimensions
3. The deployment is identifiable as a distinct system (not a general technology category)
4. The system directly affects individuals (not purely internal analytics)

Exclusion criteria:
- Purely hypothetical or speculative systems
- No verifiable public record (rumour, anecdote only)
- Duplicate of an already-coded case
- Systems only described in academic papers with no deployment evidence

## Step 2: Source Identification and Quality Rating

For each candidate case:
1. Identify at least one primary source (see source quality rubric)
2. Record all sources in `data/raw/sources_manifest.csv`
3. Assign a source quality score 0–4 (see `docs/source_quality_rubric.md`)
4. Record the access date and archive URL for each source

## Step 3: Coding the Case Record

Complete all fields in `data/processed/csa_lite_cases.csv` using the
data dictionary (`docs/data_dictionary.md`).

For each scoring dimension:
- Assign a score of 0, 1, or 2 based on the scoring rubric
- If evidence is insufficient, leave the score null
- Always provide a rationale, even for null scores
- Set the confidence level (high/medium/low/unknown)

## Step 4: Annex III Mapping

Map each case to an EU AI Act Annex III area using the mapping rubric
(`docs/annex_iii_mapping_rubric.md`). Assign:
- `annex_mapping_type`: direct / analogous / comparator / unclear
- `annex_mapping_confidence`: high / medium / low / unknown
- `annex_mapping_rationale`: non-empty explanation

## Step 5: Validation

Run `csalite validate --input data/processed/csa_lite_cases.csv` before
finalising any batch of cases. Resolve all errors. Review warnings.

## Step 6: Last Verified Date

Record the date on which the case record was last checked against primary
sources (ISO format YYYY-MM-DD) in `last_verified_date`.

## Intercoder Reliability

Where resources permit, a second independent coder should review a random
sample (≥10% of cases) and compute:
- Krippendorff's alpha for ordinal scores
- Percent agreement for categorical fields (annex_iii_area, deployer_type)

Target: α ≥ 0.70 for score dimensions.

## Ambiguity Flags

Use `ambiguity_flags` to record any unresolved ambiguities that do not
constitute exclusion grounds. Examples:
- "Vendor identity unclear"
- "Deployment scale not officially confirmed"
- "System may have changed since reporting"

## Data Ethics

- Do not record any personal data about individuals affected by systems
- `affected_population` describes populations (e.g., "welfare claimants") not named persons
- `public_record_excerpt` must be drawn from publicly available documents
- Maximum 500 words in `public_record_excerpt`

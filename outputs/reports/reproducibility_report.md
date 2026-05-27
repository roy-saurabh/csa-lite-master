# CSA-Lite v0.2.2 — Reproducibility Report

_Generated: 2026-05-27T10:39:03_

> **Disclaimer:** CSA-lite does not produce legal classifications, compliance determinations, conformity assessments, or validated harm predictions. EU AI Act Annex III categories are used only as an analytical reference frame for grouping documented deployments by use area. The Context Severity Index is a transparent structured-coding output derived from public-record evidence. It is not a legal risk class. Public records may be incomplete, biased, contested, or outdated.

---

## Run Metadata

- **Package version:** 0.2.2
- **Dataset version:** 0.2.0
- **Cases processed:** 45
- **Input file:** `data/processed/csa_lite_cases.csv`
- **Output root:** `outputs`
- **Run timestamp:** 2026-05-27T10:39:03

## Versioning Note

> The 45-case corpus is fixed as dataset version 0.2.0. The v0.2.2 release updates the software pipeline, generated manuscript outputs, validation report, case audit report, artifact manifest, documentation, and Zenodo archive without changing the 45-case corpus.

## Command

```
csalite all --input data/processed/csa_lite_cases.csv --outdir outputs
```

*(Canonical form: `csalite all --input data/processed/csa_lite_cases.csv --outdir outputs`)*

## Python Environment

- **Python:** 3.13.7 (main, Aug 14 2025, 11:12:11) [Clang 17.0.0 (clang-1700.0.13.3)]
- **pandas:** 3.0.3
- **numpy:** 2.4.6
- **matplotlib:** 3.10.9
- **pydantic:** 2.13.4
- **pandera:** 0.31.1
- **typer:** 0.26.1
- **rich:** unknown

## Expected Outputs

### Tables

- ✓ `table_1_csalite_dimensions.csv`
- ✓ `table_2_source_quality_scale.csv`
- ✓ `table_3_corpus_composition_by_annex_area.csv`
- ✓ `table_4_within_category_variance.csv`
- ✓ `table_5_dimension_level_patterns.csv`
- ✓ `table_6_evidence_confidence_by_dimension.csv`
- ✓ `table_7_sensitivity_summary.csv`
- ✓ `table_8_matched_case_contrasts.csv`

### Supplementary Tables

- ✓ `supp_table_s1_full_case_corpus.csv`
- ✓ `supp_table_s2_scored_cases.csv`
- ✓ `supp_table_s3_sensitivity_per_case.csv`
- ✓ `supp_table_s4_sources_manifest.csv`
- ✓ `supp_table_s5_annex_mapping_rationales.csv`
- ✓ `supp_table_s6_validation_summary.csv`
- ✓ `supp_table_s7_case_audit_flags.csv`

### Figures

- ✓ `fig_1_pipeline_architecture.png`
- ✓ `fig_1_pipeline_architecture.svg`
- ✓ `fig_2_corpus_by_annex_area.png`
- ✓ `fig_2_corpus_by_annex_area.svg`
- ✓ `fig_3_context_severity_by_annex_area.png`
- ✓ `fig_3_context_severity_by_annex_area.svg`
- ✓ `fig_4_dimension_heatmap.png`
- ✓ `fig_4_dimension_heatmap.svg`
- ✓ `fig_5_evidence_confidence_matrix.png`
- ✓ `fig_5_evidence_confidence_matrix.svg`
- ✓ `fig_6_sensitivity_comparison.png`
- ✓ `fig_6_sensitivity_comparison.svg`

# Manuscript Alignment

This document maps each element of the companion code repository to the
corresponding section, table, or figure in the manuscript.

## Paper Reference

> "Context-Sliced AI Assurance Lite: A Reproducible Public-Records Framework
> for Deployment-Conditioned Risk Analysis of AI Systems"
> MDPI Electronics, 2025.

## Code → Manuscript Mapping

| Code element | Manuscript location |
|---|---|
| `src/csalite/scoring.py::score_row` | Section 3.2: CSA-lite Scoring |
| `src/csalite/scoring.py::compute_evidence_completeness_index` | Section 3.3: Evidence Completeness |
| `src/csalite/sensitivity.py` | Section 3.4: Sensitivity Analysis |
| `src/csalite/analysis.py::table_1_corpus_composition` | Table 1 |
| `src/csalite/analysis.py::table_2_within_category_variance` | Table 2 |
| `src/csalite/analysis.py::table_3_dimension_patterns` | Table 3 |
| `src/csalite/analysis.py::table_4_missingness_by_category` | Table 4 |
| `src/csalite/analysis.py::table_5_sensitivity` | Table 5 |
| `src/csalite/analysis.py::table_6_high_variance_pairs` | Table 6 |
| `src/csalite/analysis.py::table_7_review_flags` | Table 7 |
| `src/csalite/plots.py::fig_1_pipeline_architecture` | Figure 1 |
| `src/csalite/plots.py::fig_2_corpus_by_annex_area` | Figure 2 |
| `src/csalite/plots.py::fig_3_context_severity_by_annex_area` | Figure 3 |
| `src/csalite/plots.py::fig_4_dimension_heatmap` | Figure 4 |
| `src/csalite/plots.py::fig_5_missingness_matrix` | Figure 5 |
| `src/csalite/plots.py::fig_6_sensitivity_band_changes` | Figure 6 |
| `src/csalite/plots.py::fig_7_source_quality_distribution` | Figure 7 |
| `src/csalite/plots.py::fig_8_dimension_mean_scores` | Figure 8 |
| `schemas/case.schema.json` | Appendix A: Data Schema |
| `docs/scoring_rubric.md` | Appendix B: Scoring Rubric |
| `docs/annex_iii_mapping_rubric.md` | Appendix C: Annex III Mapping |

## Reproducibility

All outputs in `outputs/` are deterministic given the same input data.
Sort order is always by `case_id`. Random seed for jitter: `RANDOM_SEED=42`.

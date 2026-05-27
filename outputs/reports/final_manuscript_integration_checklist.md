# CSA-Lite v0.2.1 — Final Manuscript Integration Checklist

_Generated: 2026-05-27 | Package v0.2.1 | Dataset v0.2.0 | 45 cases_

> The artifact manifest in `outputs/reports/manuscript_artifact_manifest.json` records the filename, generation command, dataset version, release version, and SHA-256 hash of each table and figure used in the manuscript.

---

## 1. Exact Table Files Generated

| Manuscript Label | Filename | Rows | SHA-256 (first 16 chars) | Status |
|-----------------|----------|------|--------------------------|--------|
| Table 1 | `outputs/tables/table_1_csalite_dimensions.csv` | 8 | `3a514f144357d92e` | PASS |
| Table 2 | `outputs/tables/table_2_source_quality_scale.csv` | 5 | `d7a717c5b5bd913f` | PASS |
| Table 3 | `outputs/tables/table_3_corpus_composition_by_annex_area.csv` | 9 | `6d6f81e1c8fba5d2` | PASS |
| Table 4 | `outputs/tables/table_4_within_category_variance.csv` | 9 | `c7dc3d1c255a1ba5` | PASS |
| Table 5 | `outputs/tables/table_5_dimension_level_patterns.csv` | 8 | `2636232223aa441d` | PASS |
| Table 6 | `outputs/tables/table_6_evidence_confidence_by_dimension.csv` | 8 | `041aa0e5176c72f7` | PASS |
| Table 7 | `outputs/tables/table_7_sensitivity_summary.csv` | 9 | `948ca27ec5a5bc71` | PASS |
| Table 8 | `outputs/tables/table_8_matched_case_contrasts.csv` | 4 | `3003ee53dbe68e88` | PASS |

### Supplementary Tables

| Supplementary Label | Filename | Status |
|--------------------|----------|--------|
| Supp Table S1 | `outputs/tables/supp_table_s1_full_case_corpus.csv` | PASS |
| Supp Table S2 | `outputs/tables/supp_table_s2_scored_cases.csv` | PASS |
| Supp Table S3 | `outputs/tables/supp_table_s3_sensitivity_per_case.csv` | PASS |
| Supp Table S4 | `outputs/tables/supp_table_s4_sources_manifest.csv` | PASS |
| Supp Table S5 | `outputs/tables/supp_table_s5_annex_mapping_rationales.csv` | PASS |
| Supp Table S6 | `outputs/tables/supp_table_s6_validation_summary.csv` | PASS |
| Supp Table S7 | `outputs/tables/supp_table_s7_case_audit_flags.csv` | PASS |

---

## 2. Exact Figure Files Generated

| Manuscript Label | Filename (PNG) | Filename (SVG) | Status |
|-----------------|----------------|----------------|--------|
| Figure 1 | `outputs/figures/fig_1_pipeline_architecture.png` | `outputs/figures/fig_1_pipeline_architecture.svg` | PASS |
| Figure 2 | `outputs/figures/fig_2_corpus_by_annex_area.png` | `outputs/figures/fig_2_corpus_by_annex_area.svg` | PASS |
| Figure 3 | `outputs/figures/fig_3_context_severity_by_annex_area.png` | `outputs/figures/fig_3_context_severity_by_annex_area.svg` | PASS |
| Figure 4 | `outputs/figures/fig_4_dimension_heatmap.png` | `outputs/figures/fig_4_dimension_heatmap.svg` | PASS |
| Figure 5 | `outputs/figures/fig_5_evidence_confidence_matrix.png` | `outputs/figures/fig_5_evidence_confidence_matrix.svg` | PASS |
| Figure 6 | `outputs/figures/fig_6_sensitivity_comparison.png` | `outputs/figures/fig_6_sensitivity_comparison.svg` | PASS |

---

## 3. Captions to Use in Manuscript

**Figure 1.** CSA-lite Analysis Pipeline Architecture. Public-record cases are screened, consolidated, mapped to EU AI Act Annex III use areas where applicable, coded across eight deployment-context dimensions, validated against schema and consistency rules, scored through the Context Severity Index, subjected to sensitivity analysis, and exported as manuscript tables, figures, and a reproducibility report. Source: `outputs/figures/fig_1_pipeline_architecture.{png,svg}`.

**Figure 2.** Corpus Composition by Annex III Analytical Area. Bars show the number of documented cases per analytical area. Source: `outputs/figures/fig_2_corpus_by_annex_area.{png,svg}`.

**Figure 3.** Context Severity Index by Annex III Analytical Area. Boxplots show within-category variation in deployment-context severity under the neutral unknown-handling rule. CSI is a structured-coding output, NOT a legal risk class. Source: `outputs/figures/fig_3_context_severity_by_annex_area.{png,svg}`.

**Figure 4.** CSA-lite Dimension Score Heatmap. Rows represent documented AI deployment cases; columns represent the eight CSA-lite dimensions. Cell values are ordinal scores (0–2). No missing values in v0.2.0 corpus. Source: `outputs/figures/fig_4_dimension_heatmap.{png,svg}`.

**Figure 5.** Evidence Confidence Matrix by Case and Dimension. Blue intensity represents evidence confidence level (high/medium/low). Source: `outputs/figures/fig_5_evidence_confidence_matrix.{png,svg}`.

**Figure 6.** Sensitivity Comparison Across Missing-Value Rules. All 45 cases fall on the y=x diagonal, confirming no band sensitivity to missing-value handling (no unknown values in v0.2.0 corpus). Source: `outputs/figures/fig_6_sensitivity_comparison.{png,svg}`.

---

## 4. Manuscript Values Verified (All PASS)

| Claim | Expected | Actual | Test | Status |
|-------|---------|--------|------|--------|
| N cases | 45 | 45 | test_n_equals_45 | PASS |
| Direct mappings | 36 | 36 | test_direct_mappings_equals_36 | PASS |
| Analogous mappings | 2 | 2 | test_analogous_mappings_equals_2 | PASS |
| Comparator mappings | 7 | 7 | test_comparator_mappings_equals_7 | PASS |
| Source quality Medium | 5 | 5 | test_source_quality_medium_equals_5 | PASS |
| Source quality High | 26 | 26 | test_source_quality_high_equals_26 | PASS |
| Source quality Very High | 14 | 14 | test_source_quality_very_high_equals_14 | PASS |
| CSI min | 7 | 7 | test_csi_min_equals_7 | PASS |
| CSI max | 16 | 16 | test_csi_max_equals_16 | PASS |
| CSI median | 12 | 12 | test_csi_median_equals_12 | PASS |
| CSI mean | 12.07 | 12.0667 (rounds to 12.07) | test_csi_mean_within_rounding_tolerance | PASS |
| Severity low | 0 | 0 | test_severity_bands_distribution | PASS |
| Severity moderate | 2 | 2 | test_severity_bands_distribution | PASS |
| Severity high | 16 | 16 | test_severity_bands_distribution | PASS |
| Severity severe | 27 | 27 | test_severity_bands_distribution | PASS |
| All 8 dims coded for all 45 | True | True | test_all_dimensions_fully_coded_no_missing | PASS |
| Missingness rate = 0 | 0 | 0 | test_all_dimensions_fully_coded_no_missing | PASS |
| No band changes across rules | True | True | test_no_band_changes_under_any_assumption | PASS |
| Confidence weight decision_criticality | 0.93 | 0.9320 | test_evidence_confidence_weights | PASS |
| Confidence weight autonomy | 0.95 | 0.9471 | test_evidence_confidence_weights | PASS |
| Confidence weight vulnerability | 0.83 | 0.8338 | test_evidence_confidence_weights | PASS |
| Confidence weight oversight | 0.77 | 0.7733 | test_evidence_confidence_weights | PASS |
| Confidence weight recourse | 0.80 | 0.7960 | test_evidence_confidence_weights | PASS |
| Confidence weight scale | 0.98 | 0.9849 | test_evidence_confidence_weights | PASS |
| Confidence weight opacity | 0.89 | 0.8942 | test_evidence_confidence_weights | PASS |
| Confidence weight monitoring | 0.86 | 0.8564 | test_evidence_confidence_weights | PASS |

---

## 5. Values Requiring Correction

**None.** All manuscript claims verified against generated data (135 tests pass).

---

## 6. DOI and GitHub Metadata Status

| Item | Value | Status |
|------|-------|--------|
| Software DOI (version) | 10.5281/zenodo.20404302 | In README, CITATION.cff, .zenodo.json — CONSISTENT |
| Concept DOI | 10.5281/zenodo.20403165 | In .zenodo.json — PRESENT |
| GitHub clone URL | https://github.com/roy-saurabh/csa-lite-master | In README — CORRECT |
| CITATION.cff version | 0.2.1 | CORRECT |
| CITATION.cff DOI | 10.5281/zenodo.20404302 | CORRECT |
| .zenodo.json version | 0.2.1 | CORRECT |
| .zenodo.json upload_type | software | CORRECT |
| .zenodo.json journal claim | None (not present) | CORRECT (no premature publication claim) |
| Article DOI | Not yet assigned | CORRECT (manuscript under review) |

**Action required before Zenodo upload:** Verify that DOI 10.5281/zenodo.20404302 is the actual reserved version DOI on Zenodo (not placeholder). Ensure the archive is uploaded to Zenodo before or at submission.

---

## 7. License Status

| Item | License | Status |
|------|---------|--------|
| Main codebase | CC BY 4.0 | In LICENSE file |
| Data | CC BY 4.0 | In README and pyproject.toml |
| CITATION.cff | CC-BY-4.0 | CONSISTENT |
| .zenodo.json | cc-by-4.0 | CONSISTENT |

**Note:** CC BY 4.0 is consistent throughout. For code, MIT or Apache 2.0 is more standard in open-source practice, but CC BY 4.0 is permissible. If submitting to MDPI, verify journal data license requirements. No inconsistency currently present.

---

## 8. Reference Audit Status

See `outputs/reports/reference_audit_checklist.md` for full checklist.

- 22 VERIFIED references
- 6 NEEDS-CHECK (missing DOI/URL or access date — fix before submission)
- 5 FLAG (require manual verification: refs 11, 12, 26, 28, 31)

**Key flags:**
- Ref 11: European AI Office guidance URL/document reference needs verification
- Ref 12: JRC132833 DOI needs verification (CEN-CENELEC JTC 21)
- Ref 28: System cards citation is arXiv preprint — check if peer-reviewed version available
- Ref 31: WEF AI Procurement report — add access date and verify exact URL/title

---

## 9. Blocking Issues

**None.** All 135 tests pass. All 8 tables, 7 supplementary tables, and 6 figures (PNG+SVG) generated. All CLI commands work. Versioning is consistent (package v0.2.1, dataset v0.2.0).

---

## 10. Major Issues

1. **Zenodo DOI must be live at submission:** DOI 10.5281/zenodo.20404302 is listed throughout but must be verified as a live, accessible Zenodo record before or at manuscript submission. If the record has not yet been uploaded, do so before final submission.

2. **6 references need DOI/URL/access date:** Refs 4, 7, 13, 14, 22, 23 lack DOI or URL. Fix before MDPI submission (MDPI style requires URLs and access dates for web sources).

3. **5 references need manual verification:** Refs 11, 12, 26, 28, 31 (see reference audit checklist).

---

## 11. Minor Issues

1. **Manuscript test count:** The manuscript text (Section 3.7) cites "122-test suite" but the updated suite has 135 tests. Update the manuscript text before submission: change "122-test suite" to "135-test suite".

2. **Reproducibility report command:** The command shown in `reproducibility_report.md` says `csa-lite all` (with a hyphen) instead of `csalite all` (CLI entry point). Minor cosmetic issue in the report; does not affect reproducibility.

3. **CLI Reference Table in README:** Table mentions "Figs 1–8" (was the old figure count). Fixed in README to say "Figs 1–6".

---

## 12. Final PASS/FAIL Recommendation

**PASS — READY FOR SUBMISSION** with these pre-submission actions:

1. Upload Zenodo archive and verify DOI 10.5281/zenodo.20404302 is live
2. Update manuscript text: "122-test suite" → "135-test suite"  
3. Fix 6 references missing DOI/URL/access date (refs 4, 7, 13, 14, 22, 23)
4. Manually verify 5 flagged references (refs 11, 12, 26, 28, 31)

All generated outputs are reproducible from the committed dataset via `csalite all`. All 135 automated tests pass. All manuscript numerical claims are verified against the generated data.

---

## Command to Reproduce All Outputs

```bash
git clone https://github.com/roy-saurabh/csa-lite-master.git
cd csa-lite-master
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q  # Should report 135 passed
csalite all --input data/processed/csa_lite_cases.csv --outdir outputs
```

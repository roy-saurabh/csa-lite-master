# outputs/

Generated outputs from the CSA-lite analysis pipeline.

All files in this directory are generated and are not version-controlled
(excluded via .gitignore). Regenerate using `csalite all`.

## Subdirectories

| Directory | Contents |
|-----------|----------|
| `tables/` | Analysis tables (CSV) corresponding to Tables 1-7 in the manuscript |
| `figures/` | Manuscript figures (PNG + SVG) |
| `reports/` | Validation and scoring summary reports (Markdown) |

## Regenerating Outputs

```bash
# Full pipeline
csalite all --input data/processed/csa_lite_cases.csv --outdir outputs/

# Individual steps
csalite analyze --input data/processed/scored_cases.csv --outdir outputs/tables/
csalite figures --input data/processed/scored_cases.csv --outdir outputs/figures/
```

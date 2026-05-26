# CSA-Lite: Context-Sliced AI Assurance Lite

**Reproducible Public-Records Framework for Deployment-Conditioned Risk Analysis of AI Systems**

Companion code for the MDPI Electronics paper:

> "Context-Sliced AI Assurance Lite: A Reproducible Public-Records Framework
> for Deployment-Conditioned Risk Analysis of AI Systems"
> *Electronics*, MDPI, 2026.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20403166.svg)](https://doi.org/10.5281/zenodo.20403166)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Disclaimer

> **CSA-lite does not produce legal classifications, compliance determinations,
> conformity assessments, or validated harm predictions. EU AI Act Annex III
> categories are used only as an analytical reference frame for grouping
> documented deployments by use area. The Context Severity Index is a
> transparent structured-coding output derived from public-record evidence.
> It is not a legal risk class. Public records may be incomplete, biased,
> contested, or outdated.**

---

## What is CSA-Lite?

CSA-lite is a reproducible public-records analysis methodology for structured
coding of AI system deployments using publicly documented evidence. It provides:

- A **structured coding framework** with 8 scoring dimensions (0–2)
- A **Context Severity Index (CSI)** — a transparent aggregate score
- A **sensitivity analysis** for handling missing evidence
- A **fully automated pipeline** from coded CSV to figures and tables

CSA-lite uses EU AI Act Annex III areas as an analytical typology, not for
legal compliance assessment.

---

## Repository Structure

```
csa-lite-mdpi-electronics/
  README.md              -- This file
  LICENSE                -- CC BY 4.0
  CITATION.cff           -- Citation metadata
  pyproject.toml         -- Package configuration
  requirements.txt       -- Dependencies
  .gitignore
  .pre-commit-config.yaml

  data/
    raw/                 -- Original source files
    interim/             -- Working extraction notes (not version-controlled)
    processed/           -- Final coded datasets (add cases here)

  schemas/               -- JSON schemas for data validation
  src/csalite/           -- Python package source
  notebooks/             -- Jupyter notebooks for exploration
  outputs/               -- Generated tables, figures, reports
  tests/                 -- Test suite with synthetic fixtures
  docs/                  -- Methodology documentation
  paper_txt/             -- Source paper text (pre-existing)
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/placeholder/csa-lite-mdpi-electronics.git
cd csa-lite-mdpi-electronics

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install in development mode
pip install -e ".[dev]"

# Verify
csalite version
```

---

## Quick Start

```bash
# 1. Validate the dataset
csalite validate --input data/processed/csa_lite_cases.csv

# 2. Score cases
csalite score \
  --input data/processed/csa_lite_cases.csv \
  --output data/processed/scored_cases.csv \
  --jsonl-output data/processed/scored_cases.jsonl

# 3. Run the full pipeline
csalite all \
  --input data/processed/csa_lite_cases.csv \
  --outdir outputs/
```

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `csalite validate` | Validate case data against coding rules |
| `csalite score` | Compute CSI and scoring fields |
| `csalite analyze` | Generate analysis tables (Tables 1–7) |
| `csalite figures` | Generate manuscript figures (Figs 1–8) |
| `csalite sensitivity` | Generate sensitivity analysis |
| `csalite report` | Generate Markdown summary report |
| `csalite all` | Run full pipeline |

---

## Running Tests

```bash
pytest tests/ -v --tb=short
```

Tests use synthetic fixture data only (`tests/fixtures/`). No production data is required.

---

## Adding Case Data

1. Code cases following `docs/coding_protocol.md`
2. Add records to `data/processed/csa_lite_cases.csv`
3. Add all sources to `data/raw/sources_manifest.csv`
4. Run `csalite validate` to check the data
5. Run `csalite all` to generate outputs

See `docs/data_dictionary.md` for all field descriptions.

---

## Documentation

| Document | Description |
|----------|-------------|
| `docs/coding_protocol.md` | Case identification and coding procedures |
| `docs/data_dictionary.md` | Field-by-field descriptions |
| `docs/scoring_rubric.md` | Scoring rubric for all 8 dimensions |
| `docs/source_quality_rubric.md` | Source quality scoring guide |
| `docs/annex_iii_mapping_rubric.md` | Annex III mapping guidance |
| `docs/reproducibility.md` | Reproducibility guide |
| `docs/limitations_and_disclaimers.md` | Limitations and ethical disclaimers |
| `docs/manuscript_alignment.md` | Code-to-manuscript mapping |

---

## Citation

If you use this code or methodology, please cite:

```bibtex
@article{csalite2025,
  title   = {Context-Sliced AI Assurance Lite: A Reproducible Public-Records
             Framework for Deployment-Conditioned Risk Analysis of AI Systems},
  journal = {Electronics},
  year    = {2025},
  publisher = {MDPI},
}
```

See `CITATION.cff` for complete citation metadata.

---

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

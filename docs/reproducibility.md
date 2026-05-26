# Reproducibility Guide

## Overview

This repository is designed to be fully reproducible given the same input data.
All analyses, figures, and tables are generated deterministically from
`data/processed/csa_lite_cases.csv`.

## Reproducibility Guarantees

1. **Sort order:** All DataFrames are sorted by `case_id` before writing
2. **Random seed:** `RANDOM_SEED = 42` is used for all jitter in figures
3. **No network calls:** No production code makes network requests
4. **Pinned dependencies:** `requirements.txt` specifies version floors
5. **Deterministic scoring:** Scoring functions are pure with no side effects

## Environment Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

# 2. Install the package in development mode
pip install -e ".[dev]"

# 3. Verify installation
csalite version
```

## Running the Full Pipeline

```bash
# Validate the coded dataset
csalite validate --input data/processed/csa_lite_cases.csv

# Score the cases
csalite score \
  --input data/processed/csa_lite_cases.csv \
  --output data/processed/scored_cases.csv \
  --jsonl-output data/processed/scored_cases.jsonl

# Generate all tables, figures, and reports
csalite all \
  --input data/processed/csa_lite_cases.csv \
  --outdir outputs/
```

## Running Tests

```bash
pytest tests/ -v --tb=short
```

## Notebook Execution

```bash
jupyter notebook notebooks/01_dataset_overview.ipynb
```

## Known Non-Reproducibility

- Figures may render slightly differently across operating systems due to
  font rendering differences. SVG output is more portable.
- Timestamps in report headers will differ across runs (intentionally).

## Archival

The data and code are archived on Zenodo with a DOI. The archived version
corresponds to the state of the repository at submission.

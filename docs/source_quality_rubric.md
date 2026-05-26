# Source Quality Rubric

## Overview

Each case is assigned a source quality score (0–4) reflecting the
evidentiary basis for the case record. Higher scores indicate more
reliable, verified, and comprehensive documentation.

## Scoring Guide

| Score | Label | Criteria |
|-------|-------|----------|
| 0 | Very Low | Single press article; no primary source; significant factual uncertainty |
| 1 | Low | Multiple press articles from different outlets OR single secondary report; no official confirmation |
| 2 | Moderate | Secondary sources corroborated by official statement, FOI response, or regulatory document |
| 3 | High | Primary government document, audit report, or court filing; corroborated by secondary source |
| 4 | Very High | Multiple independent primary sources (government + court + audit); consistent accounts; independently verifiable |

## Source Type Hierarchy

From most to least preferred:
1. Court rulings and judicial decisions
2. Government audit reports
3. Parliamentary or regulatory documents
4. Freedom of information responses
5. Academic papers with empirical deployment evidence
6. NGO investigative reports with named sources
7. Regulatory filings and company disclosures
8. Quality journalism with named sources
9. Press articles (general)

## Recording Sources

All sources must be recorded in `data/raw/sources_manifest.csv` with:
- Full URL or DOI
- Access date
- Archive URL (e.g., Wayback Machine)
- Source type classification

## Minimum Threshold

Cases with `source_quality_score <= 1` should be reviewed carefully and
flagged with the `low_source_quality_flag`. Cases scoring 0 should only
be included if the case is otherwise well-documented via ambiguity notes.

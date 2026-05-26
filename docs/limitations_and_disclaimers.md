# Limitations and Disclaimers

## Core Disclaimer

**CSA-lite does not produce legal classifications, compliance determinations,
conformity assessments, or validated harm predictions. EU AI Act Annex III
categories are used only as an analytical reference frame for grouping
documented deployments by use area. The Context Severity Index is a
transparent structured-coding output derived from public-record evidence.
It is not a legal risk class. Public records may be incomplete, biased,
contested, or outdated.**

## What CSA-Lite Is

CSA-lite is a reproducible public-records analysis methodology. It provides:
- A structured coding framework for documenting AI deployments
- A transparent aggregate score (CSI) for comparing cases
- A sensitivity analysis for handling missing evidence
- A replicable dataset for academic research

## What CSA-Lite Is Not

CSA-lite does NOT:
- Determine legal compliance with the EU AI Act or any other regulation
- Classify AI systems as "high-risk" in any legal sense
- Predict the likelihood or severity of harm from any AI system
- Constitute legal advice or professional risk assessment
- Represent the views of any regulatory authority

## Limitations of the Methodology

### 1. Public Record Completeness
Public records may be incomplete, selective, or biased. Systems with greater
public controversy may be over-represented. Systems operating without incident
may be systematically under-documented.

### 2. Coder Subjectivity
Despite standardised rubrics, some scoring decisions involve interpretation.
Intercoder reliability is addressed through documented protocols but cannot
be fully eliminated.

### 3. Temporal Validity
AI systems change over time. A case coded in a given year may not reflect
current system capabilities, governance, or deployment status. The
`last_verified_date` field tracks currency.

### 4. Jurisdictional Scope
The EU AI Act Annex III framework was developed for EU jurisdictions. Cases
from other jurisdictions are mapped analogically. Legal scope determinations
are not made.

### 5. Source Bias
Sources are biased toward English-language, high-income country, and publicly
controversial deployments. Low-visibility and non-English cases are likely
under-represented.

### 6. CSI Interpretation
The Context Severity Index is a sum of ordinal codes. Arithmetic operations
on ordinal data have known limitations. The CSI is presented as a
structured-coding summary, not a cardinal measurement.

### 7. Missing Data
High missingness (many null scores) reduces comparability. The sensitivity
analysis and evidence completeness index are tools for transparency about
this uncertainty, not solutions to it.

## Intended Use

CSA-lite outputs are appropriate for:
- Academic research on AI deployment patterns
- Policy analysis and horizon scanning
- Comparative case studies
- Reproducibility research

CSA-lite outputs are NOT appropriate for:
- Legal compliance determinations
- Regulatory enforcement
- Individual system certification or accreditation
- Investment or commercial due diligence without independent verification

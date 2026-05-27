"""
CSA-Lite: Context-Sliced AI Assurance Lite

A reproducible public-records framework for deployment-conditioned risk analysis
of AI systems. Companion code for the MDPI Electronics paper:

  "Context-Sliced AI Assurance Lite: A Reproducible Public-Records Framework
   for Deployment-Conditioned Risk Analysis of AI Systems"

IMPORTANT DISCLAIMER
--------------------
CSA-lite does not produce legal classifications, compliance determinations,
conformity assessments, or validated harm predictions. EU AI Act Annex III
categories are used only as an analytical reference frame for grouping
documented deployments by use area. The Context Severity Index is a transparent
structured-coding output derived from public-record evidence. It is not a legal
risk class. Public records may be incomplete, biased, contested, or outdated.
"""

__version__ = "0.2.2"
__all__ = [
    "constants",
    "enums",
    "models",
    "scoring",
    "validation",
    "analysis",
    "sensitivity",
    "plots",
    "reporting",
    "io",
    "cli",
]

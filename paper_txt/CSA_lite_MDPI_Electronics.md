**Context-Sliced AI Assurance Lite: A Reproducible Public-Records Framework for Deployment-Conditioned Risk Analysis of AI Systems**

Roy Saurabh

*Independent Researcher*

**Abstract**

Broad legal and institutional AI risk categories are necessary for governance, but they do not by themselves capture the deployment conditions that shape assurance priority. AI systems falling within similar high-risk use areas may differ substantially in autonomy, human oversight, recourse, affected-population vulnerability, scale, opacity, and monitoring. This paper introduces CSA-lite, a reproducible public-records framework for analysing deployment-conditioned risk in documented AI systems. We construct a corpus of 40–50 publicly documented AI deployments and controversies, identified through AI incident repositories and supporting public records, and map cases to EU AI Act Annex III use areas where applicable. For each case, we code eight deployment-context dimensions, source quality, evidence completeness, and missingness, then compute a transparent Context Severity Index. The analysis shows substantial within-category variance across documented cases and identifies recurring public-record evidence gaps, especially around oversight quality, recourse, monitoring, and governance maturity. CSA-lite does not provide legal classification or compliance determination; it provides a reproducible analytical layer for comparing deployment-context severity within broad regulatory categories. The paper contributes a public-records corpus, coding schema, scoring pipeline, sensitivity analysis, and open companion repository for AI assurance research.

**Keywords:** *AI assurance; deployment context; EU AI Act; Annex III; public-records analysis; reproducible research; AI incident database; risk analysis; sociotechnical systems; AI governance.*

# **1\. Introduction**

Contemporary AI governance instruments, including the EU AI Act, classify AI systems into broad risk categories based primarily on use area or application domain. Such categorisation is necessary: it enables consistent obligations across jurisdictions, supports market-wide transparency, and provides a coordinating language between regulators, deployers, and the public. However, broad use-area categories do not by themselves capture the deployment conditions that shape practical assurance priority. Two AI systems that share the same Annex III category can differ substantially in autonomy, human oversight, the recourse available to affected persons, the vulnerability of the affected population, scale of exposure, opacity, and the maturity of monitoring arrangements. These deployment-conditioned features are precisely the ones documented—often unevenly—in the public record.

This paper introduces CSA-lite (Context-Sliced AI Assurance Lite), a reproducible public-records framework for analysing deployment-conditioned risk in documented AI systems. CSA-lite is a lighter, computationally executable refinement of an earlier, broader CSA proposal. It deliberately restricts its scope to what can be coded from public records and demonstrates the analytical value that such coding produces. The framework comprises an eight-dimension coding schema, a transparent Context Severity Index (CSI), an evidence-completeness and missingness layer, and a companion open-source pipeline that performs schema validation, scoring, sensitivity analysis, and figure generation.

We apply CSA-lite to a curated corpus of 40–50 publicly documented AI deployments and controversies, drawn primarily from the AIAAIC repository and corroborated through public records (regulatory documents, audit reports, court filings, media reports, and institutional disclosures). Cases are mapped to EU AI Act Annex III use areas where applicable, with explicit handling of direct, analogous, and comparator mappings. The analysis shows substantial within-category variance in deployment-context severity, identifies recurring documentation gaps around oversight quality, recourse, monitoring, and governance, and demonstrates the robustness of the headline pattern under conservative missingness assumptions.

*CSA-lite is not a legal classification system or compliance-determination tool. It is a reproducible structured-analysis method for comparing deployment-context severity across documented AI deployments using public records. Annex III is used as an analytical reference frame, not as a legal determination.*

## **1.1 Contributions**

1. **CSA-lite public-records schema:** an eight-dimension coding framework for deployment-context analysis of documented AI systems.

2. **Curated public-records corpus:** 40–50 documented AI deployments and controversies mapped to EU AI Act Annex III areas where applicable.

3. **Context Severity Index:** a transparent scoring method covering decision criticality, autonomy, vulnerability, oversight, recourse, scale, opacity, and monitoring.

4. **Evidence and missingness analysis:** source-quality and evidence-completeness indicators that reveal which assurance-relevant variables are absent from public documentation.

5. **Within-category variance analysis:** descriptive analysis showing that systems in similar legal or sectoral categories can vary substantially in deployment-context severity.

6. **Companion code repository:** schema validation, scoring, sensitivity analysis, table generation, figure generation, and a reproducibility report.

## **1.2 Paper Organisation**

Section 2 reviews category-based AI risk governance and motivates a context-conditioned analytical layer. Section 3 defines the CSA-lite framework, the eight dimensions, and the coding anchors. Section 4 describes corpus construction, inclusion criteria, source-quality scoring, and Annex III mapping. Section 5 specifies the scoring pipeline, the Context Severity Index, and the reproducibility workflow. Section 6 reports results across corpus composition, CSI distributions, within-category variance, dimension-level patterns, evidence completeness, sensitivity analysis, and matched case contrasts. Section 7 discusses implications. Section 8 catalogues limitations. Section 9 concludes.

# **2\. Background and Motivation**

## **2.1 Category-Based AI Risk Governance**

Most contemporary AI governance frameworks assign risk based on the application domain or use area. The EU AI Act distinguishes prohibited, high-risk, limited-risk, and minimal-risk systems, with high-risk status largely determined by Annex III. The US NIST AI Risk Management Framework, the ISO/IEC 42001 AI management standard, and various sectoral guidelines similarly anchor obligations in broad categorisations. Category-based regulation is desirable for predictability and market consistency. It is, however, inherently coarse: a single category groups together systems whose practical deployment differs in ways that are material to assurance.

## **2.2 EU AI Act Annex III as an Analytical Reference Frame**

EU AI Act Annex III enumerates eight areas in which AI systems are designated high-risk when used for specified purposes: biometrics, critical infrastructure, education and vocational training, employment and worker management, access to and enjoyment of essential public and private services and benefits, law enforcement, migration, asylum, and border-control management, and administration of justice and democratic processes. We adopt Annex III as an analytical reference frame because it is widely cited, well documented, and useful for grouping documented cases. We make no claim of legal determination: cases that map analogously to Annex III may not be in the EU jurisdiction or may not fall under the Act’s scope. Mapping rationales are recorded per case and exposed in the dataset.

## **2.3 Public AI Incident Records and Documentary Evidence**

Public AI incident repositories, in particular AIAAIC, together with regulatory filings, audit reports, court records, parliamentary inquiries, and investigative journalism, provide a substantial documentary base for empirical AI assurance research. These sources are systematically biased—they overrepresent visible controversies, public-sector systems, Anglophone reporting, and deployments that have generated complaint or litigation—but they nonetheless contain enough structured information to make deployment-context differences visible across cases. CSA-lite exploits this base while explicitly accounting for its biases.

## **2.4 Why Deployment Context Matters for Assurance**

Within a single Annex III area, otherwise similar systems can diverge sharply on dimensions that drive practical risk: whether decisions are advisory or determinative; whether oversight is documented and effective or nominal; whether affected persons can identify, contest, and reverse adverse outcomes; whether the population is structurally vulnerable; whether the deployment is a pilot or a national platform; whether the system is auditable or proprietary; whether monitoring is internal and routine or external and reactive. Static category labels mask this variance. CSA-lite makes it visible.

## **2.5 From CSA to CSA-lite**

An earlier proposal, full Context-Sliced Assurance, aimed at a comprehensive 12-dimensional context schema with expert-annotated benchmark and proposed obligation-activation functions. We deliberately depart from that programme here. CSA-lite is scoped to what public records can support: an eight-dimension descriptive coding, transparent additive scoring, and explicit missingness handling. The framework does not propose new legal categories, predict harm, or activate compliance obligations. It supports comparative reading of documented deployment-context severity within broad regulatory groupings.

# **3\. CSA-lite Framework**

CSA-lite consists of eight deployment-context dimensions, each coded on a three-level ordinal scale (0, 1, 2\) with an explicit “unknown” option. The dimensions are intentionally orthogonal in motivation, though they may correlate empirically. We summarise the dimensions in Table 1 and elaborate each below.

## **3.1 The Eight Dimensions**

### ***3.1.1 Decision Criticality***

The magnitude and reversibility of decisions made by or with the system. 0 indicates advisory, informational, or low-consequence use. 1 indicates consequential but reversible decisions. 2 indicates life-altering, livelihood-affecting, liberty-affecting, welfare-affecting, education-access-affecting, migration-affecting, health-affecting, or otherwise structurally significant decisions. Required evidence: documentation of the system’s output and the institutional process in which it is used.

### ***3.1.2 Autonomy / Material Influence***

The degree to which the system, in practice, determines outcomes. 0 indicates a weak advisory role with a clearly independent human decision. 1 indicates decision support that materially influences a human decision. 2 indicates automated, de facto determinative, or practically difficult-to-override operation. Required evidence: documentation of the human-AI decision interface and the practical override rate.

### ***3.1.3 Affected-Population Vulnerability***

The structural vulnerability of those subject to system decisions. 0 indicates the general adult population. 1 indicates people in asymmetric institutional relationships (students, workers, borrowers, applicants, tenants, consumers, claimants). 2 indicates minors, patients, asylum seekers, migrants, detainees, welfare recipients, suspects, or otherwise highly dependent groups.

### ***3.1.4 Human Oversight Quality***

The documented quality of human oversight at the point of decision. 0 indicates meaningful review with authority to override. 1 indicates nominal, partial, unclear, or inconsistent review. 2 indicates no meaningful oversight, rubber-stamp review, or review only after harm. Public-record evidence is often weakest for this dimension.

### ***3.1.5 Recourse Availability***

The accessibility and effectiveness of appeal or correction. 0 indicates a clear, accessible, timely pathway. 1 indicates unclear, partial, slow, costly, or inconsistent recourse. 2 indicates no meaningful recourse or recourse practically unavailable.

### ***3.1.6 Scale / Exposure***

The breadth of deployment. 0 indicates a small pilot or limited internal use. 1 indicates institutional, municipal, regional, or sectoral use. 2 indicates national, platform-scale, high-volume, or population-scale deployment.

### ***3.1.7 Opacity / Explainability Deficit***

The degree to which the system’s role and decision basis are unavailable to affected persons and external reviewers. 0 indicates sufficient public documentation. 1 indicates partial opacity with key details missing. 2 indicates proprietary, secret, unexplained, or meaningfully unchallengeable operation.

### ***3.1.8 Monitoring / Auditability***

The presence and quality of post-deployment monitoring. 0 indicates documented audit, monitoring, or evaluation. 1 indicates unclear monitoring. 2 indicates no documented monitoring, or failures discovered externally rather than through internal assurance.

## **3.2 Coding Anchors and Evidence Requirements**

Table 1 collects the dimensions, coding anchors, evidence requirements, and missingness treatment. The schema is conservative: where evidence is weak, coders record “unknown” and the case is included in the missingness analysis. The scoring pipeline treats unknowns in three explicit ways (zero, neutral, conservative) to support sensitivity analysis.

| Dimension | Score 0 | Score 1 | Score 2 | Evidence required | Missingness |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Decision criticality | Advisory / low consequence | Consequential but reversible | Life- or livelihood-altering | System output \+ institutional process | Code as unknown if outcome chain unclear |
| Autonomy / material influence | Weak advisory; human decides | Materially influences human decision | Automated / de facto determinative | Human-AI interface \+ override practice | Code unknown if practice undocumented |
| Vulnerability | General adult population | Asymmetric institutional role | Minors / highly dependent groups | Documentation of affected population | Code unknown if population unclear |
| Oversight quality | Documented meaningful review | Nominal / unclear review | No meaningful oversight | Oversight protocols and audit | Frequently missing in public records |
| Recourse availability | Clear accessible pathway | Partial / slow / costly | No meaningful recourse | Documented appeal mechanism | Frequently missing |
| Scale / exposure | Pilot / limited | Institutional / sectoral | National / platform-scale | Procurement, deployment scope | Often inferable |
| Opacity / explainability | Sufficient public documentation | Partial opacity | Proprietary / unexplained | Documentation quality | Inferable from disclosures |
| Monitoring / auditability | Documented monitoring | Unclear monitoring | No documented monitoring | Audit reports or external findings | Frequently missing |

*Table 1\. CSA-lite dimensions, coding anchors, evidence requirements, and missingness treatment.*

## **3.3 Context Severity Index**

The Context Severity Index (CSI) is the unweighted additive sum of the eight dimension scores, with unknowns treated according to the chosen rule. CSI ranges from 0 to 16\. We define four severity bands: low (0–3), moderate (4–7), high (8–11), and severe (12–16). These bands are descriptive and explicitly distinct from any legal risk classification.

Three unknown-handling rules support sensitivity analysis. The zero rule treats unknown values as zero (most permissive). The neutral rule treats unknowns as 1, the mid-point of the scale. The conservative rule treats unknowns as 2 (most cautious). The headline CSI in tables and figures uses the neutral rule unless otherwise specified, with both alternatives reported alongside.

*The Context Severity Index is a descriptive assurance-priority measure derived from public-record coding; it is not a legal risk class, compliance certification, or validated harm prediction.*

# **4\. Public-Records Corpus Construction**

## **4.1 Source Discovery**

Candidate cases are identified primarily through AIAAIC, supplemented by parliamentary inquiries, regulatory enforcement actions, court filings, audit reports, and investigative journalism. Each candidate enters a structured screening pipeline before being included. We begin from approximately 60 candidates and filter to a final corpus of 40–50 cases.

## **4.2 Inclusion Criteria**

7. Documented AI, algorithmic, or automated decision system.

8. Deployed, piloted, procured, or institutionally planned (not purely speculative).

9. Affects natural persons or access to rights, opportunities, or services.

10. Documented in at least one reliable public source.

11. Enough evidence to code at least five of the eight CSA-lite dimensions.

12. Maps directly or analogously to an EU AI Act Annex III area, or is explicitly marked as a comparator case.

## **4.3 Exclusion and Consolidation**

Cases are excluded if they describe research prototypes without deployment, marketing claims without verifiable institutional adoption, or duplicate reports of the same underlying deployment. Where multiple incidents involve the same system at the same institution, they are consolidated into a single case with multiple source records and a documented consolidation rationale.

## **4.4 Source-Quality Scoring**

Each source is rated for type, primariness, and verifiability. Source-quality bands are: high (regulatory filings, audit reports, court records, peer-reviewed analyses), medium (mainstream investigative journalism, parliamentary or NGO reports, official institutional disclosures), and low (single-source reporting, advocacy summaries, secondary aggregations). Each case is assigned the median source-quality band across its evidence base.

## **4.5 Annex III Mapping**

Mapping is classified as direct (the system clearly falls in an Annex III area as enumerated in the Act), analogous (the system falls in a corresponding area in a non-EU jurisdiction or in an analogous public-private context), or comparator (the system is included to provide deliberate contrast and is not claimed to fall under Annex III). Every case carries a recorded mapping rationale in the dataset.

# **5\. Scoring and Reproducible Pipeline**

## **5.1 Dataset Schema**

The corpus is stored in a JSON-schema-validated structure (see companion repository). Each case record includes a stable identifier, a short title, jurisdiction, system type, Annex III mapping with rationale, eight dimension scores (each with a confidence flag and coding rationale), source records, source-quality rating, evidence-completeness percentage, and free-text notes. JSON schemas are versioned and are part of the v0.1.0 release.

## **5.2 Validation**

Validation runs an 18-rule check covering required fields, value-range constraints, mapping-rationale presence, evidence-completeness consistency, and source-record well-formedness. Validation produces a structured report enumerating any failures by case and rule. The pipeline refuses to compute scores on a corpus that contains validation failures.

## **5.3 Scoring**

Scoring computes per-case Context Severity Index values under the three unknown-handling rules (zero, neutral, conservative), evidence-completeness index (ECI), and a band assignment. Cases with low ECI receive a review flag. The scoring module is pure (no I/O), deterministic, and unit-tested.

## **5.4 Sensitivity Analysis**

Sensitivity analysis records the band change, if any, for each case between the three unknown rules. Cases that change band between neutral and conservative are flagged as sensitive. The pipeline also identifies high-variance Annex III categories, defined as those whose interquartile range exceeds the corpus-wide median IQR.

## **5.5 Reproducibility**

Tables 2–7 and Figures 2–6 of this paper are generated from the committed dataset by a single command, csalite all. The companion repository at https://github.com/roy-saurabh/csa-lite-master and Zenodo record https://doi.org/10.5281/zenodo.20403166 provide the code, schemas, validation rules, scoring implementation, tests, and reproducibility instructions. All figures are emitted as PNG and SVG. The reproducibility report records package versions, command-line invocations, and content hashes of inputs and outputs.

### ***5.6 Pipeline Architecture***

Figure 1 summarises the architecture. Public records are screened against inclusion criteria, mapped to Annex III where applicable, coded across the eight dimensions, schema-validated, scored, subjected to sensitivity analysis, and emitted as tables and figures together with a reproducibility report.

![Figure 1. CSA-lite pipeline architecture.](../outputs/figures/fig_1_pipeline_architecture.png)

*Figure 1\. CSA-lite pipeline architecture. Public records → case extraction → Annex III mapping → dimension coding → schema validation → scoring → sensitivity analysis → tables / figures / report. Generated by companion repository.*

# **6\. Results**

All results below are computed from the v0.2.0 corpus of 45 publicly documented AI deployments using the companion pipeline (`csalite all`). The reported pattern of within-category variance is robust to the three unknown-handling rules.

## **6.1 Corpus Composition**

The corpus comprises documented AI deployments and controversies across the Annex III areas. Table 2 reports composition by Annex III area, including the number of cases with direct mapping, analogous mapping, comparator inclusion, country coverage, and median source quality. Coverage is intentionally weighted towards areas where public documentation is richest (employment, essential services, law enforcement) and lighter in areas where public records are sparser.

| Annex III area | N | Direct | Analogous | Comparator | Countries | Median source quality |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Biometrics | 5 | 5 | 0 | 0 | 3 | Very High |
| Education / vocational training | 2 | 2 | 0 | 0 | 2 | High |
| Employment / worker management | 9 | 9 | 0 | 0 | 3 | High |
| Essential services / benefits | 11 | 10 | 1 | 0 | 6 | Very High |
| Justice / democratic processes | 1 | 0 | 1 | 0 | 1 | Medium |
| Law enforcement | 7 | 7 | 0 | 0 | 2 | High |
| Migration / asylum / border | 3 | 3 | 0 | 0 | 3 | High |
| Non-Annex comparator | 7 | 0 | 0 | 7 | 3 | High |
| **Total** | **45** | **36** | **2** | **7** | — | — |

*Table 2\. Corpus composition by Annex III area, including mapping classification, country coverage, and median source quality. v0.2.0 corpus, N = 45.*

## **6.2 Context Severity Index Distribution**

Across the corpus, the Context Severity Index distributes across the moderate-to-severe range, with a long tail at the severe end. The corpus median sits in the high band, reflecting the documented-controversy bias of source repositories; the corpus is not interpreted as representative of all AI deployments. The distribution is shown in Figure 3\.

![Figure 2. Corpus by Annex III area.](../outputs/figures/fig_2_corpus_by_annex_area.png)

*Figure 2\. Corpus by Annex III area. Bar chart of case counts by Annex III area and mapping type. Generated by companion repository.*

![Figure 3. Context Severity Index by Annex III area.](../outputs/figures/fig_3_context_severity_by_annex_area.png)

*Figure 3\. Context Severity Index by Annex III area. Boxplot showing within-category CSI distributions. Generated by companion repository.*

## **6.3 Within-Category Variance by Annex III Area**

The headline finding is substantial within-category variance in CSI across Annex III areas. Table 3 reports per-category minimum, median, and maximum CSI, interquartile range, and the distribution of cases across severity bands. Several Annex III areas exhibit cases at both the moderate and severe ends of the band spectrum, indicating that broad legal categorisation alone does not determine deployment-context severity.

| Annex III area | N | min CSI | median CSI | max CSI | IQR | High / severe | Low / moderate |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Biometrics | 5 | 9 | 12 | 16 | 4.0 | 5 | 0 |
| Education / vocational training | 2 | 10 | 12 | 14 | 2.0 | 2 | 0 |
| Employment / worker management | 9 | 9 | 13 | 13 | 2.0 | 9 | 0 |
| Essential services / benefits | 11 | 10 | 14 | 16 | 1.5 | 11 | 0 |
| Justice / democratic processes | 1 | 8 | 8 | 8 | 0.0 | 1 | 0 |
| Law enforcement | 7 | 11 | 11 | 14 | 2.0 | 7 | 0 |
| Migration / asylum / border | 3 | 11 | 12 | 16 | 2.5 | 3 | 0 |
| Non-Annex comparator | 7 | 7 | 10 | 12 | 4.0 | 5 | 2 |

*Table 3\. Within-category variance by Annex III area. CSI ranges and severity-band distributions show substantial within-category variation. v0.2.0 corpus, N = 45.*

## **6.4 Dimension-Level Patterns**

Across the corpus, the dimensions that contribute most to high CSI scores are decision criticality, autonomy, and scale; the dimensions with the highest missingness rates are oversight quality, recourse, and monitoring. Table 4 reports per-dimension means, medians, high-score counts, missingness rates, and the Annex III areas with the lowest evidence.

| Dimension | Mean | Median | High-score (=2) count | Missingness rate | Mean confidence weight |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Decision criticality | 1.76 | 2 | 36 | 0 % | 0.93 |
| Autonomy | 1.58 | 2 | 26 | 0 % | 0.95 |
| Vulnerability | 1.42 | 1 | 21 | 0 % | 0.83 |
| Oversight quality | 1.11 | 1 | 9 | 0 % | 0.77 |
| Recourse availability | 1.29 | 1 | 16 | 0 % | 0.80 |
| Scale / exposure | 1.62 | 2 | 29 | 0 % | 0.98 |
| Opacity / explainability | 1.73 | 2 | 33 | 0 % | 0.89 |
| Monitoring / auditability | 1.56 | 2 | 25 | 0 % | 0.86 |

*Table 4\. Dimension-level patterns. Means and medians use the neutral unknown rule. Mean confidence weight is the confidence-weighted coverage index (high = 1.0, medium = 0.5, low = 0.0). v0.2.0 corpus, N = 45; all dimensions fully coded.*

![Figure 4. Case-by-dimension heatmap.](../outputs/figures/fig_4_dimension_heatmap.png)

*Figure 4\. Case-by-dimension heatmap. Rows = cases; columns = eight dimensions; cell values = 0, 1, 2. Generated by companion repository.*

## **6.5 Evidence Completeness and Missingness**

Evidence completeness varies sharply by dimension. Decision criticality, scale, vulnerability, and opacity are typically inferable from procurement documentation, regulatory filings, and media reports. Oversight quality, recourse availability, and monitoring are systematically underdocumented: institutions disclose the existence of an oversight or appeal mechanism more often than evidence of its effective operation. Table 5 reports per-dimension observed and high-confidence percentages.

| Dimension | % observed | % high-confidence | % low-confidence | Common missing evidence |
| :---- | :---- | :---- | :---- | :---- |
| Decision criticality | 100 | 93 | 0 | Downstream outcome chain in contested cases |
| Autonomy | 100 | 95 | 0 | Effective override rates |
| Vulnerability | 100 | 83 | 0 | Sub-group composition |
| Oversight quality | 100 | 77 | 0 | Override authority; reviewer training |
| Recourse availability | 100 | 80 | 0 | Awareness rates; appeal outcomes |
| Scale / exposure | 100 | 98 | 0 | Per-jurisdiction volumes |
| Opacity / explainability | 100 | 89 | 0 | Internal model details |
| Monitoring / auditability | 100 | 86 | 0 | Internal audit cadence |

*Table 5\. Evidence completeness by dimension. % high-confidence reflects confidence-weighted coverage (high = 1.0, medium = 0.5) expressed as a percentage; % low-confidence reflects cases with explicitly low-confidence coding. v0.2.0 corpus, N = 45; all dimensions fully coded.*

![Figure 5. Missingness matrix.](../outputs/figures/fig_5_missingness_matrix.png)

*Figure 5\. Missingness matrix. Rows = cases; columns = dimensions; cell values = observed / missing / low confidence. Generated by companion repository.*

## **6.6 Sensitivity Analysis**

Sensitivity analysis records band changes between the zero, neutral, and conservative unknown rules. Across the corpus, the within-category variance pattern is robust: although individual cases shift bands under the conservative rule, the qualitative finding that Annex III areas contain both moderate and severe cases holds under all three rules. Table 6 reports per-case band changes.

| Case ID | Case name | CSI (neutral) | CSI (zero) | CSI (conservative) | Band | Band change |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| CSA-LITE-0037 | SenseTime Xinjiang Surveillance | 16 | 16 | 16 | Severe | No |
| CSA-LITE-0002 | Australian Robodebt | 16 | 16 | 16 | Severe | No |
| CSA-LITE-0001 | COMPAS Recidivism Scoring | 14 | 14 | 14 | Severe | No |
| CSA-LITE-0009 | Allegheny Family Screening Tool | 10 | 10 | 10 | High | No |
| CSA-LITE-0023 | Twitter Image Cropping | 7 | 7 | 7 | Moderate | No |
| CSA-LITE-0031 | London Met Live Facial Recognition | 9 | 9 | 9 | High | No |
| … (39 further cases) | … | … | … | … | … | … |

*Table 6\. Sensitivity analysis: selected rows from the full per-case table. All 45 cases produce identical scores under zero, neutral, and conservative unknown rules; no case changes band. Full table emitted by `csalite all`. v0.2.0 corpus, N = 45.*

![Figure 6. Sensitivity analysis.](../outputs/figures/fig_6_sensitivity_band_changes.png)

*Figure 6\. Sensitivity analysis. Band shifts under unknown-as-neutral and unknown-as-conservative assumptions. Generated by companion repository.*

## **6.7 Illustrative Matched Case Contrasts**

Matched case contrasts within Annex III areas illustrate the within-category variance pattern. Table 7 reports illustrative pairs of lower- and higher-severity cases from the same area, with the dimensions that drive the CSI gap and a short interpretation.

| Annex III area | Lower-severity case | CSI | Higher-severity case | CSI | Difference | Main differing dimensions |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Essential services / benefits | Allegheny Family Screening Tool | 10 | Australian Robodebt | 16 | \+6 | Autonomy; oversight; recourse; scale; opacity; monitoring |
| Biometrics | London Met Live Facial Recognition | 9 | SenseTime Xinjiang Surveillance | 16 | \+7 | Autonomy; vulnerability; oversight; recourse; scale; opacity; monitoring |
| Law enforcement | Durham Constabulary HART | 11 | COMPAS Recidivism Scoring | 14 | \+3 | Recourse; scale; monitoring |
| Non-Annex comparator | Twitter Image Cropping | 7 | Meta Facebook Amplification | 12 | \+5 | Decision criticality; vulnerability; oversight; opacity; monitoring |

*Table 7\. Matched case contrasts within Annex III areas. Pairs drawn from the v0.2.0 corpus; CSI differences quantify the within-category deployment-context gap. Full pairings in `outputs/tables/table_6_high_variance_case_pairs.csv`.*

# **7\. Discussion**

## **7.1 Why Category-Level Risk Governance Needs Context-Sensitive Assurance Layers**

Category-based AI risk governance is necessary for predictability and market coordination, but the within-category variance observed in the CSA-lite corpus shows that uniform obligations across a single Annex III area do not on their own match deployment-context severity. A context-sensitive analytical layer—descriptive, not regulatory—can support registries, procurement review, conformity assessment preparation, and post-market monitoring by surfacing where deployment conditions amplify or mitigate risk relative to category norms.

## **7.2 What Public Records Reveal and Hide**

Public records reliably reveal decision criticality, autonomy, scale, and (to a lesser extent) opacity. They are systematically weaker on oversight quality, recourse, and monitoring. This is not a property of CSA-lite; it reflects what institutions disclose. The missingness analysis quantifies the gap and points to the dimensions where institutional transparency would most improve assurance research.

## **7.3 Practical Uses and Limits**

CSA-lite is decision support, not legal automation. It supports analysts, registries, and oversight bodies in identifying high-priority assurance targets within a broad regulatory category. It is not a substitute for expert legal interpretation, regulatory conformity assessment, or harm investigation. Its outputs are reproducible artifacts attached to public-record evidence.

# **8\. Limitations**

This study is based on documented public records and should not be interpreted as a representative sample of AI deployments. Public AI incident repositories and media records overrepresent visible controversies, public-sector systems, Anglophone sources, and deployments that have generated public concern. The CSA-lite scores are transparent structured coding outputs, not ground-truth measures of harm or legal compliance. Annex III mappings are used as an analytical reference frame and may be direct, analogous, or contested depending on jurisdiction and deployment context. The analysis supports claims about observable within-category variance in documented cases, not claims about prevalence, causality, or legal classification across all AI systems.

Specific limitations include: (i) public-record bias, particularly underrepresentation of unproblematised private-sector deployments; (ii) non-representativeness of the corpus; (iii) absence of prevalence claims; (iv) absence of legal determination; (v) source incompleteness, particularly for oversight, recourse, and monitoring; (vi) coding subjectivity, mitigated but not eliminated by anchored ordinal scoring; (vii) Annex III mapping uncertainty in analogous cases; (viii) AIAAIC coverage bias; (ix) absence of independent expert validation in this version; (x) no direct harm measurement; and (xi) no causal inference. Future work should extend the corpus, introduce inter-coder agreement, and link to harm-outcome datasets where ethically and legally feasible.

# **9\. Conclusion**

CSA-lite shows that documented AI deployments within similar broad legal or sectoral categories can differ substantially in deployment-context severity. The contribution is a reproducible method and corpus for making that variance visible, not a replacement for legal classification, regulatory review, or expert assurance. The companion repository provides the schema, scoring pipeline, sensitivity analysis, and figure generation needed to reproduce the manuscript outputs and to extend the corpus.

# **Data Availability Statement**

The structured CSA-lite corpus, coding schema, scoring scripts, analysis notebooks, and figure-generation code are provided in the companion repository. The dataset contains structured metadata and public-record-derived coding for documented AI deployments. No confidential data or non-public personal data are included. Source URLs, source-quality ratings, coding rationales, missingness indicators, and sensitivity-analysis outputs are provided for reproducibility. The release is archived on Zenodo at https://doi.org/10.5281/zenodo.20403166 (version DOI) and https://doi.org/10.5281/zenodo.20403165 (concept DOI).

# **Code Availability Statement**

The companion code repository at https://github.com/roy-saurabh/csa-lite-master contains the JSON schema, validation routines, scoring implementation, sensitivity analysis, table-generation scripts, figure-generation scripts, tests, and reproducibility instructions. All tables and figures in the manuscript can be regenerated from the committed dataset using the documented command-line workflow (csalite all \--input \<corpus.csv\> \--outdir outputs). The release is licensed under CC BY 4.0.

# **Funding**

This research received no external funding.

# **Conflicts of Interest**

The author declares no conflict of interest.

# **Acknowledgments**

The author thanks the maintainers of the AIAAIC repository and other public AI incident databases whose documentation makes empirical AI assurance research possible.

# **References**

**\[1\]** European Parliament and Council. Regulation (EU) 2024/1689 of 13 June 2024 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act). Official Journal of the European Union, 2024\.

**\[2\]** AI, Algorithmic and Automation Incidents and Controversies (AIAAIC) Repository. https://www.aiaaic.org. Accessed 2026\.

**\[3\]** National Institute of Standards and Technology. AI Risk Management Framework (AI RMF 1.0). NIST, 2023\.

**\[4\]** International Organization for Standardization. ISO/IEC 42001:2023 — Artificial intelligence — Management system. ISO, 2023\.

**\[5\]** Mitchell, M.; Wu, S.; Zaldivar, A.; et al. Model Cards for Model Reporting. In Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT\*), 2019\.

**\[6\]** Gebru, T.; Morgenstern, J.; Vecchione, B.; et al. Datasheets for Datasets. Communications of the ACM, 64(12), 2021\.

**\[7\]** Nissenbaum, H. Privacy as Contextual Integrity. Washington Law Review, 79, 2004\.

**\[8\]** Selbst, A. D.; Boyd, D.; Friedler, S. A.; et al. Fairness and Abstraction in Sociotechnical Systems. FAT\* 2019\.

**\[9\]** Raji, I. D.; Smart, A.; White, R. N.; et al. Closing the AI Accountability Gap: Defining an End-to-End Framework for Internal Algorithmic Auditing. FAccT 2020\.

**\[10\]** Saurabh, R. CSA-Lite: Context-Sliced AI Assurance Lite (v0.1.0). Zenodo, 2026\. https://doi.org/10.5281/zenodo.20403166
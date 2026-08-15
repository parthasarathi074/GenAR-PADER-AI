\# GenAR-PADER-AI Analytical Pipeline



\## Phase 1 — Drug Normalization



Standardizes drug information from the source ICSR data.



Output includes normalized drug records and drug alignment

information.



\---



\## Phase 2 — Reaction Normalization



Standardizes reported reaction terminology and prepares reaction

information for integration.



\---



\## Phase 3 — Structure Validation



Validates normalized datasets before case-level integration.



\---



\## Phase 4 — Case Integration



Constructs the integrated ICSR case dataset.



Validated integrated case count:



\*\*1,024 cases\*\*



\---



\## Phase 5 — Pharmacovigilance Screening



Performs descriptive screening of reaction patterns associated with

the Bisoprolol case cohort.



This phase does not perform causal inference.



\---



\## Phase 6 — Signal Pattern Analysis



Creates detailed profiles for candidate reaction patterns including:



\- case frequency

\- seriousness

\- demographic distributions

\- country distributions

\- product/co-medication patterns



\---



\## Phase 7 — Evidence \& Reporting



Transforms candidate profiles into structured evidence datasets.



\---



\## Phase 8 — Structured Pharmacovigilance Reporting



Produces standardized reporting records and candidate report cards.



\---



\## Phase 9 — Decision Support



Assigns review-priority categories.



Categories:



\- higher\_priority\_candidate

\- moderate\_priority\_candidate

\- lower\_priority\_candidate



These are review priorities and are not confirmed safety signals.



\---



\## Phase 10 — Controlled Reporting



Generates:



\- machine-readable report

\- human-readable pharmacovigilance report

\- controlled GenAI context

\- reporting rules



\---



\## Phase 11 — Application Output



Produces frontend/API-ready data including:



\- dashboard summary

\- candidate table

\- candidate detail cards

\- application metadata

\- API payload



\---



\## Phase 12 — Release Validation



Performs final end-to-end validation and creates the release package.



The release includes SHA-256 checksums and release metadata.



\---



\# Final Validated Dataset



Integrated cases:



\*\*1,024\*\*



Candidate reactions:



\*\*8\*\*



Highest review-priority candidate:



\*\*Acute kidney injury\*\*



Reported cases:



\*\*22\*\*



\---



\# Analytical Restrictions



The pipeline intentionally preserves the following restrictions:



```text

Comparator available            = False

ROR available                   = False

PRR available                   = False

Frequency interpreted incidence = False

Causality established           = False

Disproportionality established  = False

Confirmed signal established    = False

Drug interaction established    = False


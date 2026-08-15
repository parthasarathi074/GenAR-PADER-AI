\# GenAR-PADER-AI API



Default development server:



`http://127.0.0.1:8000`



\---



\## Health Check



\### GET /health



Checks whether the backend and release datasets are available.



\---



\## Dashboard



\### GET /api/dashboard



Returns the Phase 11 dashboard summary.



Example information:



\- total safety reports

\- Bisoprolol cases

\- candidate reaction count

\- priority distribution

\- top candidate

\- analytical status



\---



\## Candidates



\### GET /api/candidates



Returns the validated candidate reaction records.



The current release contains eight candidate reactions.



\---



\## Assistant Status



\### GET /api/assistant/status



Returns configuration and evidence-scope information for the GenAI

assistant.



Example status fields include:



```json

{

&#x20; "assistant": "GenAR-PADER-AI",

&#x20; "configured": true,

&#x20; "scope": "validated\_project\_evidence\_only",

&#x20; "web\_search": false,

&#x20; "external\_medical\_sources": false,

&#x20; "causality\_established": false,

&#x20; "disproportionality\_established": false

}


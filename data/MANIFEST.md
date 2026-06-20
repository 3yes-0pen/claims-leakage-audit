# Data Manifest — Claims Leakage Audit

| File | Grain | Source Notebook | Last Generated | Rows |
|---|---|---|---|---|
| `failure_node_payer_heatmap.parquet` | One row per payer_id x upstream_failure_node | 03_denial_forensics.ipynb | 2026-06-19 | 19 rows |
| `failure_node_provider_heatmap.parquet` | One row per practice_name x upstream_failure_node | 03_denial_forensics.ipynb | 2026-06-19 | 20 rows |
| `urgency_triage_queue.parquet` | One row per denial_id, active appeal window only | 03_denial_forensics.ipynb | 2026-06-19 | 611 rows |
|---|---|---|---|---|
| `intervention_matrix.parquet` | One row per intervention (4 rows total) | 05_intervention_modeling.ipynb | 2026-06-19 | 4 rows |
|---|---|---|---|---|
| `denial_fingerprint.parquet` | One row per patient_segment x carc_code | 06_pop_health.ipynb | 2026-06-19 | 27 rows |
| `specialty_interpretations.parquet` | One row per specialty (authored commentary) | 06_pop_health.ipynb | 2026-06-19 | 5 rows |
|---|---|---|---|---|
| `waterfall_summary.parquet` | One row per waterfall stage (8 rows total) | 07_financial_integrity.ipynb | 2026-06-19 | 8 rows |
# Tasks - scheduled exports migration

| ID | Task | Status | Depends on |
|----|------|--------|------------|
| T1 | Job definition for export-dataset | done | - |
| T2 | Streaming CSV writer | done | T1 |
| T3 | Idempotency key and export_runs migration (staging) | done | T1 |
| T4 | Apply migration 0042 in production (DBA window, ticket DBA-5521) | blocked: needs a DBA window | T3 |
| T5 | XLS export above 1M rows (policy decision first) | blocked: needs product decision | T2 |
| T6 | Pool sizing 3 to 6 workers | blocked: needs budget decision | T2 |
| T7 | Email template approval and wiring | in progress: waiting for Marketing | T2 |
| T8 | Map the 3 unmapped cron jobs (export_weekly_xls, export_audit, export_adhoc) | todo | - |
| T9 | Per-tenant rollout: nimbus-internal, then Acme, then all tenants | todo | T4, T5, T6, T7 |
| T10 | Decommission legacy cron | todo | T8, T9 |
| T11 | Fix flaky test_export_cancel | todo (low priority) | - |

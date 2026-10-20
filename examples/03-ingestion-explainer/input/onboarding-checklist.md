# Week-one checklist for new ingestion engineers

- [ ] Get access: repo permissions, the `ingestion-dev` cloud subscription, on-call rota (read-only for now), Grafana.
- [ ] Clone the repos: `ingest-api`, `ingest-workers`, `schema-contracts`, `platform-docs`.
- [ ] Run the local stack: `docker compose up`, then the e2e smoke test with `POLICY_MODE=strict`.
- [ ] Read the runbooks: `replay-dlq` and `quarantine-release`.
- [ ] Upload a sample file that passes, and one that fails validation. Watch both in the Catalog UI.
- [ ] Shadow the on-call engineer for one shift.
- [ ] Pick up a starter ticket: INGEST-310 (add a column type to the Schema Registry validator) or INGEST-322 (improve the quarantine email wording).
- [ ] Join the weekly ingestion sync (Wednesdays 10:00 CET) and the Friday incident review.

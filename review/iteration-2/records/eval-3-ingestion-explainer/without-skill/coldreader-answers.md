1. This is an onboarding guide to the ingestion platform, which validates customer-uploaded files
   (CSV, Parquet, JSON Lines) against an agreed schema, transforms them and publishes them as queryable tables.
   Its message: five design rules (Catalog is the source of truth, idempotent workers, immutable Versions, validation
   failure is expected, tenant scoping) explain most of the design, so learn them first.

2. No decision requested. Action: the reader (a new ingestion engineer) reads the first three sections on day one (about
   15 minutes; presumably Short version, Vocabulary, How a file moves) and keeps the rest as reference; the week-one plan
   is in "Your first week". Items marked "Check" should be confirmed; by whom and by when is not stated.

3. Not ranked by the document; my order: (1) infrastructure failures, retried then sent to the DLQ, which pages on-call;
   (2) duplicate delivery, harmful unless workers are idempotent; (3) Catalog and queue disagreeing on status;
   (4) "Version" meaning three things (confusion in tickets, PRs, Support); (5) unconfirmed Assumption/Check items
   in the guide itself (contents not stated here).

4. Three stages joined by a message queue: Upload → Validate → Transform and publish; the outcome is a Version status in
   the Catalog plus an email to the dataset owner. Validation checks the Schema Registry contract; failures go to the
   Quarantine Store, infrastructure failures to the DLQ. The Transform Worker publishes and writes the Lineage record to
   the Catalog; the Policy Engine decides access. A Tenant owns Datasets; each upload is an immutable Version.

5. 5 GB max file size; 15-minute publish target for files up to 1 GB; about 15 minutes to read the first three sections;
   "accurate as of October 2026". Counts it stresses: 5 rules, 3 stages, 6 vocabulary terms, 3 meanings of "Version".

6. "How a file moves through the platform", where the screen cuts off: I expect Figure 1 (a left-to-right map) and a
   stage-by-stage walkthrough of Upload → Validate → Transform and publish. Caution: Figure 1 is referenced but no image
   was in the folder, so I could not see it. After that I would read "The components" (Catalog, Schema Registry, etc.).

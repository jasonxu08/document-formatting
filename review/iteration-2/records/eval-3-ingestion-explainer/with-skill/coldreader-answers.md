1. A first-week explainer for new ingestion engineers on how an upload becomes a published table: each upload is an
   immutable Version that background workers move from received to validated to published (or quarantined).
   Main message: everything is asynchronous; the Catalog, not the Message Queue, records a Version's status.

2. None explicit. The header says "draft for team review" (written for Priya and later new ingestion engineers) but
   names no decision, owner or deadline. Its only guidance is reading paths and closing the section 6 gaps early;
   who does that and by when: not stated.

3. The doc does not rank them; in its table order: (1) waiting on the HTTP call or Message Queue instead of reading the
   Catalog; (2) "fixing" a Version instead of uploading a new one; (3) paging people over quarantines or ignoring the
   DLQ; (4) duplicate side effects on redelivery (at-least-once delivery); (5) local Policy Engine mocked allow-all, so
   a change passes locally but is denied for real. Also: notes not yet checked against code or dashboards.

4. Flow: Customer -> Uploader API (creates Version "received" in the Catalog; queues validate) -> Validation Worker
   (checks the Schema contract; sets validated/quarantined; queues transform) -> Transform Worker (writes tables and
   lineage; sets published). The Message Queue links the steps (DLQ after 3 failures); every step reports to the Catalog.
   Data model: Tenant, Dataset, Version, Schema contract, Quarantine, Lineage record; 11 components, 3 listed in this excerpt.

5. Published within 15 min for files up to 1 GB (target); typical file 50 to 500 MB, hard limit 5 GB; 3 attempts, then
   the DLQ pages on-call; quarantine kept 30 days, raw uploads 1 year. Also: 6 concepts, 11 components.
   Dates: document dated 2026-10-17; source notes "true as of October 2026".

6. Section 1, "Six concepts and eleven components" (~3 min), which is also where this excerpt cuts off. I expect the rest
   of the component table, Figure 2 (Raw Zone, Policy Engine, Schema Registry, Notifier) and the vocabulary that all
   later sections reuse. After that, section 2 (the four steps, with the status after each).

# Cold-reader answers

Source: only `top.md` (first 60 lines) and `report.assets/flow-map.png` (Figure 1).

## 1. What it is about, and the main message
It is a first-week explainer, written for new ingestion engineers such as Priya, on how the ingestion platform turns a customer's uploaded file into a published, queryable table: the file moves asynchronously through three stages (Uploader API, Validation Worker, Transform Worker) linked by a Message Queue, and is checked against the dataset's schema contract. Its main message is one mental model plus a few traps - above all that the Catalog, not the Message Queue, is the source of truth for an upload's status, and that a file failing validation is routine rather than a platform fault - and it is a draft (medium confidence) with seven points still to be confirmed by Sam.

## 2. Decision or action requested
- Sam is asked to confirm seven open points (listed in section 6, which I cannot see). No deadline is visible.
- Readers (new engineers) are given a week-one to-do list: get access; run the local stack and the e2e smoke test with `POLICY_MODE=strict`; upload one passing and one failing sample file; take INGEST-310 or INGEST-322; also read two runbooks, shadow one on-call shift and join two standing meetings. The only time frame is "week one" - no calendar date.
- No approval or decision is requested of anyone else (as far as I can see).

## 3. Most important risks or problems
The document does not rank them; this is the order of its "trap" table, which I take as importance order.
1. Trusting the Message Queue over the Catalog when they disagree about an upload's status.
2. Duplicate delivery (the queue is at-least-once): workers that are not idempotent cause duplicate effects and make a dead-letter queue (DLQ) replay unsafe.
3. Misreading failures: treating a bad file as a platform fault (it is routine: quarantined, dataset owner emailed), while exhausted retries (3 attempts, then DLQ) page the on-call engineer.
4. Editing a Version, or shipping a breaking schema change as a new Version (it needs a new dataset major version).
5. A green local run that real permissions would reject (the Policy Engine is mocked as allow-all unless `POLICY_MODE=strict`).
- About the document itself: nothing is checked against code, runbooks or dashboards, and seven points are unconfirmed (which seven is not visible to me).

## 4. Key components/steps and how they relate
- Flow (Figure 1, top to bottom): Customer uploads a file -> Uploader API (stage 1; sets `received`, queues "validate") -> Message Queue (at-least-once) -> Validation Worker (stage 2; checks the file against the schema contract).
  - Pass: sets `validated` and queues "transform" through the Message Queue -> Transform Worker (stage 3; writes tables to the Curated Zone, sets `published`).
  - Fail: copies the file to the Quarantine Store and sets `quarantined`.
- The Catalog is written to by all three stages and is the source of truth for status.
- Infrastructure failure: after 3 failed attempts a message is dead-lettered to the DLQ, which pages the on-call engineer.
- Vocabulary: Tenant -> Dataset (has a schema contract) -> Version (one upload, immutable); a Lineage record links a published Version to its raw file and the contract version it was validated with.
- The Raw Zone, Policy Engine, Schema Registry and Notifier are left out of Figure 1 (drawn in Figure 2, not visible to me), so I cannot say how they connect.

## 5. Numbers and dates that matter
- "Key facts" line: published within 15 minutes for files up to 1 GB (typical 50-500 MB, maximum 5 GB); 3 attempts, then the DLQ pages on-call; quarantine kept 30 days, originals 1 year; every timestamp is UTC.
- Dates: 2026-10-19 (appears to be the document date); the notes are "true as of October 2026".
- Counts: 7 points to confirm; 11 components in 3 groups; 6 concepts and 4 statuses; 3 stages; 20 settings in the config reference.
- Week one: tickets INGEST-310 / INGEST-322, 2 runbooks, 1 on-call shift, 2 standing meetings.
- Not visible: whether the 15 minutes is a target or a guarantee, and what applies to files between 1 GB and 5 GB.

## 6. What I would read next
Section 4, "A bad file is routine and a broken dependency pages on-call": it is the section the trap table points to most (3 of 5 rows). I expect to find how a failed file is quarantined (30-day retention, owner emailed), how retries lead to the DLQ and an on-call page, why workers must be idempotent, how to replay the DLQ safely, and what to do when the queue and the Catalog disagree. After that: section 3 for the timings, and section 2 for the four components Figure 1 omits.

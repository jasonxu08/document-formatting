# How the ingestion platform works

*A first-week explainer for engineers joining the ingestion team.*

After reading this you should be able to explain how an uploaded file becomes a published table, what happens when something fails, and what to do on each day of your first week.

- **Audience:** new ingestion engineers. It assumes strong backend skills and no knowledge of our platform.
- **Based on:** the team's architecture notes and week-one checklist. The facts were accurate as of October 2026.
- **Reading time:** about 20 minutes for the main text. The appendices are reference material.

## How to use this page

- **On day one,** read [What the platform does](#what-the-platform-does) through [The pipeline, stage by stage](#the-pipeline-stage-by-stage). That is the mental model everything else hangs off.
- **Before you need them:** read [The life of a Version](#the-life-of-a-version) and [When things go wrong](#when-things-go-wrong) before you shadow on-call, and [Running it locally](#running-it-locally) before your first PR.
- **As reference:** [Shared services and stores](#shared-services-and-stores), [Numbers to know](#numbers-to-know), [Gotchas](#gotchas) and the appendices.
- **Your week:** [Your first week](#your-first-week) turns the onboarding checklist into a day-by-day plan.

Callouts labelled **Assumption** or **Open question** mark places where the source notes were silent or unclear. They are collected in [Appendix B](#appendix-b-assumptions-and-open-questions). When you learn an answer, fix the page.

## What the platform does

Customers upload data files (CSV, Parquet or JSON Lines). The platform checks each file against an agreed schema, transforms it and publishes it as a queryable table. The whole flow is asynchronous: nobody waits on an HTTP call for the result. The dataset owner is told afterwards, either that the data is published or that the file was quarantined and why.

**upload → validate → transform → publish**, with a quarantine exit for files that fail validation.

For a sense of scale: typical files are 50 to 500 MB, the maximum is 5 GB, and the target is to publish a file within 15 minutes for files up to 1 GB. This page covers the path from upload to published table. It doesn't cover how customers query the published tables.

### Six ideas that explain most of the design

1. **Asynchronous and queue-driven.** The Uploader API stores the file, records it, queues a message and is done. Workers do the rest.
2. **The Catalog is the source of truth for status, not the queue.** If the two disagree, trust the Catalog.
3. **Delivery is at-least-once, so every worker must be idempotent.** The same message can arrive twice, and handling it twice must be harmless.
4. **A failed validation is an outcome, not an error.** The file is quarantined and the owner is told. Only infrastructure failures are retried. If the retries run out, the message goes to the dead-letter queue (DLQ), which pages on-call.
5. **Nothing is overwritten.** The Raw Zone and every Version are immutable. "Fixing" data means uploading a new Version.
6. **Everything is scoped to a tenant, and the Policy Engine decides who may do what:** at upload, in the Catalog, and row by row in the Curated Zone.

## The big picture

![Architecture diagram: a customer uploads to the Uploader API, which passes work through the Message Queue to the Validation Worker and then the Transform Worker. The workers and the Uploader API use the Raw Zone, the Catalog, the Schema Registry, the Policy Engine, the Quarantine Store, the Curated Zone and the Notifier. Each numbered step is described in the text below.](images/architecture-overview.png)

*Figure 1. The components and the path of one upload. The step numbers are explained in [The pipeline, stage by stage](#the-pipeline-stage-by-stage).*

Three components do the work: the **Uploader API**, the **Validation Worker** and the **Transform Worker**. A **Message Queue** connects them. Files live in three stores: the **Raw Zone**, the **Quarantine Store** and the **Curated Zone**. Four supporting services keep records and answer questions: the **Catalog**, the **Schema Registry**, the **Policy Engine** and the **Notifier**.

## Core concepts

Learn these terms first. Most of this page is written in them.

| Term | What it means | Keep in mind |
|---|---|---|
| **Tenant** | A customer organisation. | Everything is scoped to a tenant. |
| **Dataset** | A named collection a tenant owns, with a Schema contract. Example: `acme/orders`. | The owner recorded in the Catalog is told when one of its Versions is quarantined or published. |
| **Version** | One upload of a dataset. | Immutable. Re-uploading creates a new Version and never overwrites. |
| **Schema contract** | The agreed column names, types and constraints for a dataset. | Validation checks every file against it. The Schema Registry stores it, versioned. |
| **Quarantine** | Where a Version goes when validation fails. | The Version stays visible in the Catalog with status `quarantined`. The file is held in the Quarantine Store for 30 days. |
| **Lineage record** | Links a published Version to its raw file and to the Schema contract version it was validated with. | Written by the Transform Worker when it publishes. |

> **Three different "versions".** The word appears in three places, and mixing them up causes real confusion.
>
> - A **Version** (capital V) is one immutable upload of a dataset. It is the thing that has a status.
> - A **Schema contract version** is one revision of a dataset's contract. The Schema Registry versions contracts and only allows backward-compatible changes.
> - A **dataset major version** is what a *breaking* schema change creates. A breaking change is never just a new Version (see [Gotchas](#gotchas)).

## The pipeline, stage by stage

A file passes through three stages. The step numbers match [Figure 1](#the-big-picture). One rule applies to every step: delivery is at-least-once, so each step must be safe to repeat. The notes don't describe how the existing workers guarantee that. Read how they do it early in your first week.

### Stage 1: upload (Uploader API)

The Uploader API is the only public entry point. For each upload it does five things:

- **1. Receive and authenticate.** The upload arrives and the caller is authenticated.
- **2. Check policy.** It asks the Policy Engine whether this tenant may upload to this dataset.
- **3. Store the file.** It streams the file into the Raw Zone.
- **4. Record the Version.** It creates a Version in the Catalog with status `received`.
- **5. Queue the work.** It puts a `validate` message on the Message Queue.

After step 5 nobody waits on the result. Settings: `MAX_UPLOAD_MB` = 5120 (the hard limit) and `UPLOAD_CHUNK_MB` = 16 (streaming chunk size).

### Stage 2: validate (Validation Worker)

When a `validate` message arrives, the Validation Worker does this:

- **6. Read and check.** It reads the file from the Raw Zone, fetches the dataset's Schema contract from the Schema Registry and checks the file against it.
- **7a. If the file passes,** it sets the Version to `validated` and puts a `transform` message on the queue.
- **7b. If the file fails,** it copies the file to the Quarantine Store, sets the Version to `quarantined` and has the Notifier tell the dataset owner why. This Version goes no further.

Settings: `VALIDATION_BATCH_ROWS` = 50000 (rows per batch), `VALIDATION_TIMEOUT_S` = 600 (per message) and `SCHEMA_CACHE_TTL_S` = 300 (Schema Registry reads are cached). Rows longer than `MAX_ROW_BYTES` (1 MiB) are rejected, but the notes don't say where that is enforced or whether one over-long row fails the whole file (see [Appendix B](#appendix-b-assumptions-and-open-questions)).

### Stage 3: transform and publish (Transform Worker)

When a `transform` message arrives, the Transform Worker does this:

- **8. Convert and write.** It reads the validated file from the Raw Zone, converts it to the curated format and writes it to the Curated Zone (the lakehouse tables).
- **9. Record lineage and publish.** It writes a Lineage record to the Catalog (which Version came from which raw file and which Schema contract version), then sets the status to `published`.
- **10. Notify.** It asks the Notifier to email the owner.

Settings: `TRANSFORM_TIMEOUT_S` = 1800 (per message), `PARQUET_ROW_GROUP_MB` = 128 (transform output) and `CURATED_PARTITION_BY` = `upload_date` (default partitioning).

## Shared services and stores

| Component | What it does | Who uses it | Worth knowing |
|---|---|---|---|
| **Message Queue** | Carries `validate` and `transform` messages between the stages. | The Uploader API and the Validation Worker put messages on it. Both workers take them off. | At-least-once delivery, so workers must be idempotent. A message gets 3 attempts, then goes to the DLQ. |
| **Catalog** | Metadata store: Datasets, Versions, statuses, lineage and owners. Also has the Catalog UI. | All three stages. Support, through the UI. | **The source of truth for status.** It asks the Policy Engine who may see a dataset. Workers cache Catalog reads for 60 s. |
| **Schema Registry** | Stores the Schema contract for each dataset, versioned. | The Validation Worker. | Only backward-compatible changes are allowed. A breaking change needs a new dataset major version. Reads are cached for 300 s. |
| **Policy Engine** | Answers "may this user or tenant do X on dataset Y?" | The Uploader API (upload rights), the Catalog (who can see a dataset) and the Curated Zone (row-level rules). | Runs in `strict` mode everywhere except local dev. Answers are cached for 30 s. |
| **Raw Zone** | Immutable blob storage holding every original upload. | The Uploader API writes. Both workers read. | Kept for 1 year. |
| **Quarantine Store** | Holds files that failed validation. | The Validation Worker writes. Support can release files. | Kept for 30 days. |
| **Curated Zone** | The lakehouse tables customers query. | The Transform Worker writes. Customers read. | Row-level access is enforced by the Policy Engine. |
| **Notifier** | Sends emails and webhooks. | The Validation Worker (on quarantine) and the Transform Worker (on publish). | Fire-and-forget: a failed email never fails a Version. It retries twice. |

> **Caches mean changes aren't instant.** Policy answers are cached for 30 s, Catalog reads in workers for 60 s and Schema Registry reads for 300 s. A change to a policy, a Catalog record or a Schema contract can take up to that long to take effect. Keep that in mind when you test one.

## The life of a Version

![Status diagram: a Version starts as received, becomes validated when the file passes its Schema contract and published once the tables and Lineage record are written. A file that fails the Schema contract goes from received to quarantined. Messages that run out of attempts go to the dead-letter queue.](images/version-lifecycle.png)

*Figure 2. The four statuses a Version can have in the Catalog, and which component sets each one.*

| Status | Set by | What it means | What happens next |
|---|---|---|---|
| `received` | Uploader API (step 4) | The file is in the Raw Zone and a `validate` message is queued. | The Validation Worker picks it up. |
| `validated` | Validation Worker (step 7a) | The file passed its Schema contract and a `transform` message is queued. | The Transform Worker picks it up. |
| `quarantined` | Validation Worker (step 7b) | The file failed validation. A copy is in the Quarantine Store for 30 days and the owner has been told why. | The pipeline stops here for this Version. The owner uploads a corrected file as a new Version, or support releases the file with the `quarantine-release` runbook (the notes don't say what release does to the status). |
| `published` | Transform Worker (step 9) | The data is in the Curated Zone and the Lineage record exists. | Done. The owner is emailed (step 10). |

> **Assumption:** the notes list these four statuses and no others, so there is no separate "failed" status. A Version whose message has been dead-lettered is assumed to keep the last status it reached, `received` or `validated`. Check this in the Catalog code before you rely on it.

## When things go wrong

There are two very different kinds of failure, and the platform handles them differently.

**A validation failure is an expected outcome, not a platform error.** The file didn't meet its Schema contract, so it is quarantined (step 7b) and the owner is told why. Nothing is retried and nobody is paged.

**An infrastructure failure is retried, then dead-lettered.** The notes give blob timeouts and an unavailable Schema Registry as examples. The message is retried with back-off delays of 30 s, 2 min and 10 min. After the last failed attempt it goes to the DLQ, and a DLQ depth of 1 or more pages the on-call engineer.

> **Open question: three attempts or three retries?** The notes say both "3 attempts" and "retried 3 times", and they list three back-off delays. Three attempts in total would need only two waits. Confirm which it is before you reason about timing, for example how long a message can sit in back-off.

**A failed notification is not a failed Version.** The Notifier is fire-and-forget. It retries twice, and a failed email never fails a Version.

**When the Catalog and the queue disagree, trust the Catalog.** The queue only delivers work. It isn't a record of what happened, and because delivery is at-least-once, a message can reappear after its Version has already moved on.

### Quick triage

| What you see | What it usually means | What to do |
|---|---|---|
| A Version is `quarantined`. | Its file failed the Schema contract. This is expected, and the owner has already been told why. | Not an incident. The owner uploads a corrected file as a new Version, or support releases the file with the `quarantine-release` runbook. |
| A page for the DLQ (depth of 1 or more). | A `validate` or `transform` message used up its attempts, probably on an infrastructure failure such as a blob timeout or an unavailable Schema Registry. | Find out why it failed, then replay with the `replay-dlq` runbook. Replaying is safe because workers are idempotent. |
| A Version has sat in `received` or `validated` for longer than expected (the target is 15 minutes for files up to 1 GB). | The next stage hasn't finished. Its message may be waiting, being retried or dead-lettered. | Read the Catalog first, then look at the queue and the DLQ. This row is derived from the pipeline, not taken from a runbook. |
| The owner says they never got the email. | The Notifier is fire-and-forget, and a failed email never fails a Version. | Look up the Version's status in the Catalog and answer from that. |

## Numbers to know

| What | Value |
|---|---|
| Typical file | 50 to 500 MB |
| Maximum file | 5 GB (`MAX_UPLOAD_MB` = 5120) |
| Validation, p95 | 40 s for a 1 GB file |
| Transform, p95 | 6 min for a 1 GB file |
| Target | Published within 15 min, for files up to 1 GB |
| Retry back-off | 30 s, 2 min, 10 min, then the DLQ |
| Quarantine retention | 30 days |
| Raw Zone retention | 1 year (365 days) |

The notes give no time target for files between 1 GB and 5 GB.

Rough arithmetic from these numbers (derived here, not stated in the notes): for a 1 GB file the two p95 times add up to about 6 min 40 s, which leaves about 8 minutes of the 15-minute target for queueing and everything else. A single 10-minute back-off would blow that target on its own, so the target describes the happy path.

## Running it locally

```bash
docker compose up
```

- It starts emulators for the **queue** and **blob storage**.
- The **Policy Engine is mocked as allow-all** unless you set `POLICY_MODE=strict`. Deployed environments run `strict`.
- **Before you open a PR, run the end-to-end (e2e) smoke test with `POLICY_MODE=strict`.** Allow-all never denies anything, so a permissions bug can pass locally and fail for real.

> **Open question:** the notes don't give the smoke-test command, say how `POLICY_MODE` is passed to the stack, or list what else the local stack contains (the Catalog, Schema Registry and Notifier). Check the repo READMEs and ask the team.

## Gotchas

1. **Versions are immutable.** People will ask you to "fix" a Version. You can't: they upload a new one.
2. **A breaking schema change needs a new dataset major version, not a new Version.** The Schema Registry only allows backward-compatible changes to a Schema contract.
3. **All timestamps are UTC, including in the Catalog UI.** Support gets confused about this every week, so convert before you compare with a customer's local time.
4. **Local runs don't enforce permissions by default.** See [Running it locally](#running-it-locally): use `POLICY_MODE=strict` for the smoke test before every PR.
5. **The Notifier is fire-and-forget.** A failed email never fails a Version, so when an owner says they got no email, check the Catalog before you assume something broke.
6. **Quarantine retention is 30 days. Raw Zone retention is 1 year.** People mix these up. The quarantined copy expires after 30 days, and the original upload stays in the Raw Zone for a year.

## Your first week

This turns the team's week-one checklist into a plan. All eight checklist items are here.

### The repos

> **Assumption:** the notes list four repos but not what is in them. This mapping is inferred from the names, so check each README on day one.

| Repo | Probably contains |
|---|---|
| `ingest-api` | The Uploader API |
| `ingest-workers` | The Validation Worker and the Transform Worker |
| `schema-contracts` | Schema contract definitions |
| `platform-docs` | Platform documentation. The notes don't say where the runbooks live. |

### A suggested plan

> **Assumption:** the checklist has no order. Only the Wednesday sync and the Friday incident review are fixed. This plan assumes you start on a Monday.

**Monday: get set up**

- [ ] Get access: repo permissions, the `ingestion-dev` cloud subscription, the on-call rota (read-only for now) and Grafana.
- [ ] Clone the repos: `ingest-api`, `ingest-workers`, `schema-contracts` and `platform-docs`.
- [ ] Read this page.

**Tuesday: run it**

- [ ] Run the local stack with `docker compose up`, then the end-to-end smoke test with `POLICY_MODE=strict`.
- [ ] Read the runbooks `replay-dlq` and `quarantine-release`. They cover the two recovery paths: replaying dead-lettered messages and releasing quarantined files.

**Wednesday: watch it work**

- [ ] Upload a sample file that passes, and one that fails validation. Watch both in the Catalog UI.
  - The passing file should go `received`, `validated`, `published`, and leave a Lineage record in the Catalog.
  - The failing file should go `received`, `quarantined`.
  - Notice that timestamps are UTC, and read what the owner is told (INGEST-322 is about that wording).
- [ ] Join the weekly ingestion sync (Wednesdays, 10:00 CET as written in the notes; the calendar invite is authoritative).

**Thursday: start contributing**

- [ ] Pick up a starter ticket:
  - **INGEST-310** adds a column type to the Schema Registry validator. It sits in the Schema contract and validation path (stage 2).
  - **INGEST-322** improves the quarantine email wording. It sits on the quarantine path (step 7b, from the Validation Worker to the Notifier).
  - Both are on the validate-and-quarantine path, which is the part of the platform to know best by Friday.

**Friday: close the loop**

- [ ] Join the Friday incident review. The notes give no time, so check the calendar.
- [ ] If your starter ticket is ready, run the smoke test with `POLICY_MODE=strict` before you open the PR.

**Whenever the rota allows**

- [ ] Shadow the on-call engineer for one shift. Re-read [When things go wrong](#when-things-go-wrong) first.

### You've got it when you can answer these

1. Which four statuses can a Version have, and which component sets each one? ([The life of a Version](#the-life-of-a-version))
2. A customer asks you to "fix" a Version. What do you tell them? ([Core concepts](#core-concepts), [Gotchas](#gotchas))
3. A Version has been in `validated` for 40 minutes. Where do you look first, and which source wins if the queue disagrees? ([When things go wrong](#when-things-go-wrong))
4. What happens to a message after its last failed attempt, and who is woken up? ([When things go wrong](#when-things-go-wrong))
5. Why must the smoke test run with `POLICY_MODE=strict` before a PR? ([Running it locally](#running-it-locally))
6. How long do we keep a quarantined file, and how long the original upload? ([Numbers to know](#numbers-to-know))

## Appendix A: configuration reference

Defaults as of October 2026. Check the deployed configuration before you rely on them. The names look like environment variables, but the notes don't say where they are set. Suffixes: `_S` is seconds, `_MB` megabytes, `_DAYS` days and `_BYTES` bytes.

| Area | Setting | Default | Notes |
|---|---|---|---|
| Size limits | `MAX_UPLOAD_MB` | 5120 | Uploader API hard limit (5 GB) |
| Size limits | `UPLOAD_CHUNK_MB` | 16 | Streaming chunk size |
| Size limits | `MAX_ROW_BYTES` | 1048576 | Rows longer than this are rejected (1 MiB) |
| Size limits | `VALIDATION_BATCH_ROWS` | 50000 | Rows per validation batch |
| Size limits | `PARQUET_ROW_GROUP_MB` | 128 | Transform output |
| Timeouts and concurrency | `VALIDATION_TIMEOUT_S` | 600 | Per message (10 min) |
| Timeouts and concurrency | `TRANSFORM_TIMEOUT_S` | 1800 | Per message (30 min) |
| Timeouts and concurrency | `WORKER_CONCURRENCY` | 4 | Messages per worker |
| Retries and alerting | `QUEUE_MAX_ATTEMPTS` | 3 | Then the DLQ |
| Retries and alerting | `QUEUE_BACKOFF_S` | 30,120,600 | Retry delays in seconds (30 s, 2 min, 10 min) |
| Retries and alerting | `DLQ_ALERT_THRESHOLD` | 1 | Page when DLQ depth is at least this |
| Retries and alerting | `NOTIFIER_RETRY` | 2 | Fire-and-forget retries |
| Retention | `QUARANTINE_RETENTION_DAYS` | 30 | Quarantine Store |
| Retention | `RAW_RETENTION_DAYS` | 365 | Raw Zone |
| Caches | `CATALOG_CACHE_TTL_S` | 60 | Catalog reads cached in workers |
| Caches | `SCHEMA_CACHE_TTL_S` | 300 | Schema Registry reads cached |
| Caches | `POLICY_CACHE_TTL_S` | 30 | Policy answers cached |
| Behaviour | `POLICY_MODE` | strict | `allow-all` only in local dev |
| Behaviour | `CURATED_PARTITION_BY` | upload_date | Default partitioning of curated tables |
| Behaviour | `LOG_LEVEL` | info | |

## Appendix B: assumptions and open questions

### Assumptions made in this page

1. **Repo contents** are inferred from the repo names only.
2. **The day-by-day order** is a suggestion. The checklist has none, and a Monday start is assumed.
3. **There is no fifth status.** A Version whose message is dead-lettered is assumed to keep its last status.
4. **The timing arithmetic** in [Numbers to know](#numbers-to-know) is derived from the notes' figures, not stated in them.

### Open questions

Nobody has answered these yet. Ask the team (Sam wrote the source notes), then update this page.

1. **Attempts or retries?** Does "3 attempts" mean the first try plus two retries, or the first try plus three? Why are there three back-off delays?
2. **What does `quarantine-release` do?** Does a released file go back through validation or straight to transform, and what status does the Version show afterwards?
3. **What does "rejected" mean for `MAX_ROW_BYTES`?** Is the row dropped or the whole file quarantined, and which stage enforces it?
4. **Who owns what?** Which of the Catalog, Schema Registry, Policy Engine, Notifier and Message Queue does the ingestion team own, and which does it only use? That decides where a change goes.
5. **What is in the local stack?** Besides the queue and blob emulators and the mocked Policy Engine, are the Catalog, Schema Registry and Notifier real, mocked or shared? Do the week-one sample uploads go to the local stack or to `ingestion-dev`?
6. **Do maximum-size files fit?** If transform time scales linearly (6 min per GB), a 5 GB file takes about 30 minutes, which equals `TRANSFORM_TIMEOUT_S` (1800 s). The notes only give the p95 for 1 GB.
7. **How do the workers stay idempotent?** What are the idempotency keys or write patterns in the validate and transform steps?
8. **Small practicalities:** where the sample files are, the exact smoke-test command, how `POLICY_MODE` is passed to the stack, and the time of the Friday incident review.

---

*Sources: Sam's architecture notes (a working brain dump, October 2026) and the week-one checklist for new ingestion engineers. The diagram sources are in [`images/`](images/). Each `.dot` file starts with the command that regenerates its PNG.*

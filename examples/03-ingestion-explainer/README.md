# Platform explainer for a new hire

[← All examples](../README.md) · [Review of this scenario](../../review/iteration-2/eval-3-ingestion-explainer.md)

**Explainer · English.** A new engineer needs to understand how a file upload becomes a published table on an ingestion platform with eleven components. The input is architecture notes and an onboarding checklist.

> **Prompt given to both agents**
>
> New engineer Priya starts on the ingestion team on Monday. She's a strong backend dev but knows nothing about our platform. Using the notes in examples/03-ingestion-explainer/input/, write an explainer of how the ingestion platform works so she's productive in her first week. Save it as a doc we can drop into the team wiki repo.

## What the reader sees first

| Without the skill | With the skill |
|---|---|
| ![first screen without the skill](images/without-skill-first-screen.png) | ![first screen with the skill](images/with-skill-first-screen.png) |
| [Open the document](without-skill/report.md) | [Open the document](with-skill/report.md) |

The scenario was also written again with the published skill, v1.0.0: [the document](../../review/final-check/outputs/03-ingestion-explainer/report.md), gate ✅, cold reader 6/6 ([final check](../../review/final-check/README.md)).

## What to look for

- No verdict to invent: the first screen opens with the mental model as one sentence, then a picture and the handful of things that matter, each with the trap if it is missed.
- A glossary placed before the first section that uses its terms (concepts before flows).
- A component map with eleven nodes that stays legible because it is split into an overview and a zoom.

## Scores

| | Without the skill | With the skill |
|---|---|---|
| Assertions passed | 12 / 21 | 20 / 21 |
| Automatic checker | ❌ 0 Blockers · 4 Majors · 5 Minors | ✅ 0 Blockers · 0 Majors · 1 Minor |
| First section, words (budget about 300) | 239 | 289 |
| Cold reader, first 60 lines | 6 / 6 key facts | 6 / 6 key facts |

Every assertion with the grader's evidence is on the [review page](../../review/iteration-2/eval-3-ingestion-explainer.md).

## What is in this folder

| Folder | Contents |
|---|---|
| `input/` | `architecture-notes.md` (an unedited brain dump: components, concepts, numbers, failure handling, gotchas); `onboarding-checklist.md` (what the new hire should do in week one) |
| `without-skill/` | `diagrams`, `final_reply.md`, `report.md` |
| `with-skill/` | `final_reply.md`, `report.assets`, `report.evidence.md`, `report.md` |

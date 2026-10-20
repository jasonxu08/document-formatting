# Post-mortem in Chinese

[← All examples](../README.md) · [Review of this scenario](../../review/iteration-2/eval-4-postmortem-zh.md)

**Root-cause report · Chinese.** A production outage has been handled. The tech lead must decide which follow-up items to do first. The request, the notes and the raw chat log are all in Chinese, and the raw chat log must stay in the report.

> **Prompt given to both agents**
>
> 上周五（10月9日）下午的订单故障已经处理完了。时间线、服务清单和当时的群聊记录我放在 examples/04-postmortem-zh/input/ 里。请帮我写一份复盘报告，发给整个研发团队，技术负责人张伟要根据它决定先做哪些改进项。原始群聊记录也要留在报告里备查。

## What the reader sees first

| Without the skill | With the skill |
|---|---|
| ![first screen without the skill](images/without-skill-first-screen.png) | ![first screen with the skill](images/with-skill-first-screen.png) |
| [Open the document](without-skill/report.md) | [Open the document](with-skill/report.md) |

The scenario was also written again with the published skill, v1.0.0: [the document](../../review/final-check/outputs/04-postmortem-zh/report.md), gate ✅, cold reader 6/6 ([final check](../../review/final-check/README.md)).

## What to look for

- The document, its headings, labels and diagram text are in the reader's language, with no empty glyph boxes in the picture (the skill documents the CJK font pitfall).
- A root cause with confidence and basis, the impact, and the decision the tech lead has to take, all on the first screen.
- The raw chat log preserved in a collapsed archive block.

## Scores

| | Without the skill | With the skill |
|---|---|---|
| Assertions passed | 12 / 23 | 22 / 23 |
| Automatic checker | ❌ 0 Blockers · 4 Majors · 6 Minors | ✅ 0 Blockers · 0 Majors · 0 Minors |
| First section, words (budget about 300) | 359 | 283 |
| Cold reader, first 60 lines | 5 / 6 key facts | 6 / 6 key facts |

Every assertion with the grader's evidence is on the [review page](../../review/iteration-2/eval-4-postmortem-zh.md).

## What is in this folder

| Folder | Contents |
|---|---|
| `input/` | `timeline.md` (the incident timeline); `services.csv` (the services involved); `chat-log.txt` (the raw group chat during the incident) |
| `without-skill/` | `figures`, `final_reply.md`, `report.md` |
| `with-skill/` | `final_reply.md`, `report.assets`, `report.md` |

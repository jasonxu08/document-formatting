# user_notes.md - postmortem-zh, run-1 (with skill)

Deliverable: `report.md` (Chinese), with `report.assets/services.png` and `report.assets/services.dot` beside it. No sibling evidence file was created (see 2.1).

## 1. Skill instructions I followed

- Read `SKILL.md`, `assets/skeleton.md`, `references/diagrams.md` and `references/review-rubric.md` first, then ran `scripts/check_doc.py` (I did not read its source).
- **Language:** the user wrote Chinese, so the title, headings, glance-panel labels, caption, diagram text and archive labels are all Chinese. The English in the skill was treated as instructions only.
- **Step 1, audience split:** a 👤 human zone (glance panel + five numbered sections) and a 🗄️ machine/archive zone at the end with lettered blocks, each collapsed in `<details>` and opening with an italic line naming its bin and the claim it supports: A = AI-input handoff, B = raw chat log, C = diagram source and edge list. Zone markers (`<!-- zone:human|ai-input|archive -->`) are in place. Nothing a person needs to decide lives only in the archive (the source discrepancies are in human-zone Section 5).
- **Step 2, headline:** verdict (🟡), bottom line, confidence with basis, one decision (who / what / by when / recommendation, plus the cost of being wrong once), five ranked risks with severity glyph, consequence and a link.
- **Panel budget:** the first draft's panel was 504 words (checker Major C2). I cut it to 283 by shortening the bottom line, confidence, decision and caption, shrinking the reading-path link texts, dropping the separate "key facts" line (the numbers moved into the bottom line) and moving the notation line to Section 1.
- **Reading path:** "接着读" list with the section number in each link text, minutes per item, and who can stop where. Headings carry the argument. Each section opens with the question it answers and closes with "下一节 →". Linked headings contain only plain words and digits (no punctuation or emoji), and all 25 anchors resolve (checker plus my own GitHub-style slug test).
- **Concepts before flows:** a short glossary follows the mental model in Section 1; the A1–A6 IDs get short names in the decision line.
- **Diagram rule fired** (8 related services plus a push path and a retry path): embedded Graphviz PNG (Microsoft YaHei), `.dot` source beside it, alt text, caption with how-to-read and takeaway, one focal node, dashed edge for the unverified retry, edge list in archive block C. I viewed the rendered image and confirmed there are no empty boxes (1512×661 px).
- **Honesty:** "(推断)" marks inferences; every judgment carries a confidence level; derived numbers (17 and 9 person-days, 38 minutes, 69 minutes and so on) are labelled as derived; unknowns and source discrepancies are listed in Section 5.
- **Delivery hygiene:** no machine-local paths, relative links with forward slashes, blank lines after `</summary>` and `</details>`, no alert blocks, two loud blockquote headings.
- **Gate:** the final checker run is 0 Blockers, 0 Majors, 0 Minors (the first run had 1 Major and 1 Minor, both fixed). I also walked the judgment rules (A3, B2, B3, C3-C6, D2, E1-E2, F3-F4).
- The chat reply is a miniature of the glance panel.

## 2. Unclear, contradictory, or not followed

1. **Raw chat log kept inline instead of in a sibling file.** SKILL.md says material goes to `<name>.evidence.md` when a single block exceeds about 25 lines (the chat is 28 lines, and AI-input plus archive together exceed about 60). Its "self-sufficient document" exception only keeps AI-input inline and still moves archive material out. But the user explicitly asked that the original chat "stay in the report". I treated the explicit user request as overriding the rule of thumb and put it verbatim in a collapsed `<details>` block B. I checked programmatically that all 28 lines are identical to the source, in order. A strict reviewer could count this against rubric A3 ("long material in a sibling file"); the checker did not flag it.
2. **"Uppercase START HERE"** cannot apply to Chinese. I used "从这里开始" and relied on the 👤 glyph and position for loudness.
3. **Heading anchors with CJK.** "Plain words and digits" is easy in English; for Chinese I kept CJK words, avoided all punctuation in linked headings, and verified with the checker. I did not test Azure DevOps's own anchor algorithm.
4. **The 300-word panel budget is ambiguous for Chinese.** I followed the checker's count (283) rather than inventing my own conversion.
5. **Verdict glyph semantics.** 🟢/🟡/🔴 are defined as go / go-with-conditions / stop. For a postmortem I used 🟡 to mean "resolved, but the gaps that caused it are still open", which stretches the definition.
6. **In-image legend abandoned.** I tried a Graphviz legend node; the swatch cells rendered as large blobs and distorted the layout. Instead I put short status words inside the three focal nodes ("连接池上限被改成 20", etc.) and explained arrows in the caption. This meets "colour needs a legend or caption" but is not a classic legend.
7. **Skeleton marker placement.** The skeleton has only one `<!-- zone:archive -->` before block B; I added one before block C so every block starts with a marker, as SKILL.md says.
8. **Handoff block.** The rubric's A4 applies to handoff documents, not postmortems. I still included a short AI-input block A, because this document is a living one (a decision is pending and the panel will need refreshing). That was a judgment call.
9. **"By when" for the decision** is not in the sources. I assumed "before next iteration planning" and stated the assumption in Section 4.

## 3. What I am unsure about

- **Inline vs sibling chat log** (2.1): I think inline matches the user's intent, but it departs from the skill's size rule.
- **The prioritisation is my judgment.** The order (A4, A6, A3, A1, A5, then A2) rests on "what the incident evidence says each item would have changed ÷ person-days". The effects are inferences, not measurements, and are labelled so. Recommending A2 after A5 is a close call; the alternative (A2 first) is laid out in Section 4.
- **The A1 caveat** (a global range check cannot stop a value that is legitimate in test) is my inference from one chat message (15:03). It may grow A1's 3-day estimate; I flagged it for 周杰 rather than changing the estimate.
- **Source discrepancies I could not resolve:** payment CPU "about 40 minutes" (timeline) vs 69 minutes between the 14:22 and 15:31 chat messages; "about 25 minutes wasted" on the database vs 8 minutes in the chat; the alert text "已持续 5 分钟" vs the claim that the 5-second threshold delayed the alert; and the payment→order retry direction, which is absent from services.csv. The report is therefore marked as a draft and asks 赵敏/王磊 to confirm.
- **Assumptions:** that none of A1–A6 has started since 10-09 (the timeline says "待决定优先级"); that the report date is 2026-10-17 (taken from the system clock); that the people named in the "请谁核对" column are the right owners.
- **Wording:** I avoided "中断" (outage) because 3,800 failed orders and a 0.04-point availability drop suggest partial failure, so I used "故障" and "受影响".
- **Rendering:** I did not open the Markdown in VS Code or Azure DevOps; I relied on the checker, my own anchor and table checks, and viewing the PNG.
- **Length:** the human zone is 2,480 words by the checker, just under the 2,500 advice, but that is still roughly 4,000 Chinese characters. I kept it because each section ties to the decision.

Your handoff is written: `eval-2-dual-audience-handoff\with_skill\outputs\report.md`, with the diagram, an evidence file and copies of your three notes beside it.

**🟡 At risk.** The CSV export path is built and passed 20 staging exports, but the Tue 2026-11-10 cutover only holds if four open answers land by Fri 2026-10-30 (your own at-risk line). Nothing is done in production yet.

**Decisions Dana needs to make or route**
- Q1 XLS above 1M rows: ZIP of 1M-row files (your preference) or CSV only. Asked 2026-10-06, no answer.
- Q2 +1,200 USD/month for 6 workers so Acme's 15-minute SLA holds (21 min today with 3 exports at once).
- Q3 Marketing sign-off on the email, Q4 someone to book the DBA slot, Q5 owners for the 3 unmapped cron jobs, Q6 keep or move the cutover date.

**Top risks:** all four rollout prerequisites wait on other people and none has a date; Acme's SLA fails when 3 exports run at once on 3 workers (21 min against 15), and Acme runs several on Monday mornings; you are back Sat 7 Nov, one working day before cutover.

**Where to start:** Dana reads the panel at the top of `report.md` (about a minute), then section 3 if she is deciding. The agent starts at block A at the bottom: limits, commands, ordered steps and a decision log.

**Please check before you go:** the agent's boundaries (staging only, Dana's go-ahead for production steps) are my proposal, not yours. Your notes say leave starts 2026-10-17 but you said "from tomorrow"; I dated the document 2026-10-19 and used the return date, which agrees. Your notes name no budget holder, Marketing contact or DBA contact, so Dana will need to supply them. The skill's checker reports no blockers, majors or minors.

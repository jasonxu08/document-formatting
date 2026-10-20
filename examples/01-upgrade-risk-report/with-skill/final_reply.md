The report is done and saved as `report.md`. It recommends neither "all now" nor "all in January", but a split.

**🟡 Go with conditions: upgrade seven services before the freeze, move `auth-service` and `user-store` to January.** The seven passed staging and roll back in 10 to 15 minutes. The Identity pair has no rollback and is not ready: 2 of 148 tests fail, `user-store` was never tested, the vendor library is uncommitted, and one Identity engineer is on leave. Extended support (18,000 USD) is needed either way, so the split costs no more than waiting. Confidence is medium. It is high that the Identity pair must wait, and lower that the seven fit the schedule.

**Decisions for Marcus**
1. **Approve the split plan by Fri 2026-10-23:** I recommend approving.
2. **Order v8 extended support by Thu 2026-11-05:** I recommend ordering it.
3. **Ask the change advisory board for a freeze exception by Fri 2026-10-23:** I recommend asking.

**Top risks**
- 🔴 Upgrading the Identity pair too early: no rollback, about 4 hours to restore, every login down.
- 🟠 A slip or regression lands in the freeze, when only P1 hotfixes deploy. The Data team's week ends Fri 2026-10-30, the last working day before the freeze, so there is no slack.
- 🟠 The Identity pair runs on unpatched v8 after 2026-11-12 if extended support isn't ordered.

**Where to start:** the panel at the top of `report.md`. Stop there if you're only deciding.

**Assumptions** (labelled in the report; the extended-support ones could change the cost):
- Extended support is a flat 18,000 USD covering all of v8, and a quarter runs from 2026-11-12.
- The freeze limits production deployments only, not staging.
- Marcus can approve the spend.

For the audit trail, the supporting data sits beside the report:
- `report.evidence.md` has the full inventory, the 36-row incident log and how each number was derived.
- `report.data/` holds byte-identical copies of your three inputs, with checksums recorded in the evidence file.
- A decision record in `report.md` is ready to fill in after Friday, with update instructions for the next person.

The document checker reports no blockers or warnings on `report.md`. `user_notes.md` covers where the skill's instructions were unclear and what I'm unsure about.

Everything is in the `outputs` folder:
- `report.md`
- `report.evidence.md`
- `user_notes.md`
- `report.assets/`
- `report.data/`

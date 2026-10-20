The explainer for Priya is written, with a sibling lookup file and two diagrams. The checker finds 0 blockers, 0 majors and 0 minors on `report.md`. The sibling file gets only the expected "machine-only file" note. I checked all 49 links myself and viewed both diagrams. I couldn't test how your wiki renders the page.

**Mental model:** every upload becomes an immutable Version. Background workers advance its status from `received` to `validated` to `published`, or `quarantined` if the file is bad. The Catalog, not the queue, is the record of that status.

**The traps most likely to bite in week one:**
- Locally the Policy Engine is mocked as allow-all, so run the smoke test with `POLICY_MODE=strict` before every PR.
- Versions never change; "fixing" one means uploading a new one.
- A failed validation is expected, but a stuck message in the dead-letter queue pages on-call.

**The notes leave gaps** (section 6 of the doc). It would help to settle these before Monday:
- How many attempts a message gets: the notes say "3 attempts", "retried 3 times" and list three retry delays.
- The smoke-test command, and whether `POLICY_MODE` defaults to `strict` or allow-all locally.
- Which repo holds which component.

Everything not stated in Sam's notes is marked *derived*, *suggested* or *guess* in the text.

**Where to start reading:** the top panel takes about a minute. Then read sections 1 and 2, then section 5, which maps her week-one checklist to the page.

I put the 20-row config table and the arrow-by-arrow diagram lists in `report.evidence.md` rather than inline. If your wiki treats that as a stray page, you can paste its contents back into the doc. Move `report.md`, `report.evidence.md` and `report.assets/` together, since all links are relative.

Files are in the `outputs` folder you named:
- `report.md`
- `report.evidence.md`
- `report.assets/`
- `user_notes.md`

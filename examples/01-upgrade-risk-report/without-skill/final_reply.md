The report for Marcus is written, with the supporting data kept alongside it. It recommends splitting the upgrade rather than choosing "before the freeze" or "January".

**Recommendation:** upgrade the 7 services that passed staging before the freeze starts on 2026-11-01, with gateway last. Keep auth-service and user-store on v8 until January and order one quarter of v8 extended support ($18,000, by 2026-11-05).

The reasons, in short:
- user-store is untested.
- auth-service fails 2 of 148 tests.
- Neither can be rolled back.
- The vendor's identity library isn't committed.
- The Identity team is down to one engineer during the key weeks.

Before the first deploy on 2026-10-26, two things need confirming. Platform must confirm the seven staging passes ran against auth-service on v8, and the teams must confirm their slots. If either fails, fall back to deferring everything to January.

The audit trail is covered:
- **Evidence folder:** verbatim copies of your three inputs with checksums, the calculated numbers, and a script that regenerates them and the dependency diagram.
- **Decision record:** Section 7 of the report is blank for Marcus to fill in.

Please check three assumptions I made: the $18,000 is a flat price for a 3-month term, "P1" means SEV1-class, and the wave dates and the 2026-12-15 checkpoint (which are my proposals) are acceptable. `user_notes.md` has the structure choices and the other open points.

Files are in `<workspace>\iteration-2\eval-1-upgrade-risk-report\without_skill\run-1\outputs`:
- report.md
- user_notes.md
- evidence/
- figures/

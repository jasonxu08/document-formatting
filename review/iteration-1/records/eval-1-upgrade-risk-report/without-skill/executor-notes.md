# Notes on report.md

## 1. Structure choices and why

- **Answer first.** Marcus decides by Friday, so the Recommendation opens the report: the answer, three reasons, the four decisions he is asked to make, and how confident I am. Everything after it is support he can skip.
- **I reframed the question.** The brief was "before the freeze or January". The data points to a split: seven services now, auth-service and user-store in January. The report says so up front and compares three options (A all now, B all in January, C split) in one table. B stays as an explicit fallback, with the conditions that would trigger it.
- **Evidence headings state the point, and each point uses the form that fits it.** A dependency diagram for structure, a bar chart for the incident ranking, a timeline for the calendar squeeze, a table for the recovery comparison, and a small table that maps the four breaking changes onto the split.
- **Plan, cost, risks, assumptions and revisit triggers are separate sections**, so Marcus can see what the recommendation depends on and what would change it.
- **Audit trail built in.** A blank, append-only decision record; revision history; dates labelled as stated in the notes, proposed, or assumed (Appendix C); absolute dates throughout so it still reads correctly in six months.
- **"Keep the supporting data" is done three ways.**
  - The three source files are byte-for-byte copies in `evidence/`.
  - `analysis/analyze.py` recomputes every number and figure from them and writes derived tables, including `key-numbers.csv` (each quoted number with its definition).
  - Appendices A to C describe the files and tabulate the incident analysis.
  - All links are relative, so the folder can be dropped anywhere in the repo.
- **Portability.** Plain GitHub-flavoured Markdown tables and blockquotes, PNG figures with the `.dot` source kept, ASCII-only text. I avoided Mermaid and GitHub-only alert syntax because Azure DevOps may not render them.
- **No author line and no sign-off.** The decision record is left blank for Marcus.
- **Length.** About 4,500 words including appendices, about 3,700 before them. The first page stands alone; the evidence section is what to trim if Marcus wants it shorter.

## 2. What I was unsure about

- **Extended support terms.** Is USD 18,000 flat or per service? Is a quarter a rolling three months or a calendar quarter? I assumed flat and rolling, and set a ceiling of USD 36,000 to cover the other readings.
- **The CAB rule "already staged and tested".** I read it as "passed staging", so the seven qualify and the Identity services do not. This is the basis of the contingency request.
- **What the seven were tested against.** The notes do not say whether auth-service was v8 or v10 in those runs. In production the seven will call a v8 auth-service for the whole freeze. I made this a pre-Monday check and the one condition behind my "moderate" confidence in moving the seven now.
- **Why auth-service itself has no rollback path.** The notes tie it to the schema migration, which belongs to user-store. I flagged it and did not resolve it.
- **Proposals that nobody has agreed to.** The Phase 1 order, the 2026-10-30 date for placing the extended support order, the 2026-12-15 checkpoint, and the Phase 2 gates. The notes do not say whether Platform and Integration have capacity in the week of 2026-10-26.
- **Incident attribution.** I treated the two 2026-07-11 SEV1 rows as one event (same date, minutes and severity, and the gateway summary says "caused by"). That gives 35 events from 36 rows. Attributing three more gateway incidents to auth-service is a reading of free-text summaries.
- **Rounding.** auth-service is 44.5% of incident minutes (44.4965% underneath), so the text says "about 45%" next to the exact counts.
- **Dates.** I dated the report 2026-10-17 from the system clock and took "Friday" as 2026-10-23, as in the notes. I assumed the Identity engineer is back from Monday 2026-11-16.
- **Notes taken as given.** Staging results, rollback times, vendor timing and price were not checked against primary sources.
- **Likelihood and impact ratings in the risk table** are my judgment and are labelled as such.

To regenerate the figures and tables: `python analysis/analyze.py` from the folder (matplotlib and Graphviz `dot` needed).

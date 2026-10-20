# Notes on report.md

## 1. Structure choices and why

- **Answer first.** Marcus decides by Friday, so Section 1 gives the recommendation, the four decisions requested and the two gates. Section 2 (options table) completes what he needs; Sections 3 to 7 and the appendices are reference. A one-line reading guide at the top says so. Sections 1 and 2 are about 1,100 words; the whole file is about 4,500.
- **Three options, not two.** The notes ask "before the freeze or January". The data splits the nine services: seven passed staging and roll back in 10–15 minutes; auth-service and user-store did not and cannot be rolled back. I added a split option and put the comparison in one table (same rows for each option: what happens, what stays on v8, extended-support cost, worst case, what must be true, verdict) because it is a multi-attribute comparison.
- **Facts, inference and assumptions kept apart.** Section 3 states what the inputs say, with codes such as (I20) pointing to rows in `evidence/derived/key-figures.csv`. Where I connect two facts myself (the failing token-refresh tests and the Q3 token-refresh incidents; the retry-behaviour change and gateway's timeout history) the text says "inference". Assumptions are listed in 6.2. Open questions each have an owner and a needed-by date.
- **Tables only where the content is tabular** (options, service facts, dates, waves, risks, questions, incident aggregates). Bullets and short paragraphs elsewhere.
- **One figure.** The dependency map, because "auth-service is the hub and sits on user-store" is the central argument and is hard to see in a table. PNG so it renders everywhere, Graphviz source kept, alt text plus the services table as the text equivalent.
- **Audit trail built in.** A blank decision record at the end, with the instruction to keep Sections 1 to 6 as written and add dated addenda. The three inputs are copied verbatim into `evidence/source/` with SHA-256 checksums. Derived numbers are in `evidence/derived/` with how each was calculated, and `evidence/analysis.py` regenerates them and the figure. All links are relative, so the folder can move into the repo as one unit.
- **Plain Markdown.** Pipe tables, no HTML, Mermaid or GitHub-only callouts, so it renders the same in GitHub, Azure DevOps and VS Code. Dates are ISO, with the weekday where timing matters.
- **Counting rule.** The 2026-07-11 SEV1 is logged under both auth-service and gateway. Per-service tables keep both rows; event counts count it once (35 events, not 36).

## 2. What I was unsure about

- **Extended-support terms.** Flat price or per service/host? Does a quarter start at activation or follow the calendar? Renewal lead time? I assumed a flat $18,000 and a 3-month term from 2026-11-12. This decides whether C is cheaper than B and whether January needs $18,000 or $36,000.
- **The freeze rules.** The inputs do not define "P1" or say whether a rollback is exempt. I assumed P1 means SEV1-class and flagged both for CAB.
- **Which auth-service version the seven staging passes ran against.** If it was v10 with the shim, "ready" needs a re-run against v8 (Gate 1). This is the biggest hole in the recommendation.
- **Capacity.** Only the Data team's capacity is stated. I do not know whether "one week" includes production rollout, or whether Platform and Integration can take their waves.
- **What is mine, not the teams'.** The wave dates, the 2026-12-15 checkpoint, the slow-dependency check before gateway and the two gates are my proposals. So is reading `depends_on` as "caller depends on callee" and treating auth-service and user-store as a pair.
- **Data currency.** The inventory and the incident log have no as-of date, and the log ends 2026-09-28. I assumed the staging results of 2026-10-09 to 10-11 still hold.
- **Approximate figures.** The 41% share of minutes and the "about two incidents" estimate use rows as logged and the 92-day quarter as the denominator. They show scale only.
- **Rendering and checks.** I rendered the file with a local CommonMark engine and checked every table and weekday against the raw data with a second calculation. I have not seen it in your repo host. The checksum check can fail after a git line-ending conversion.
- **Unrequested additions.** The decision record and the evidence structure follow from "audit trail". They are easy to drop. There is no author line; git history carries that.

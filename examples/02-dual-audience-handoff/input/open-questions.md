# Open questions (need a human decision)

1. **XLS above 1M rows.** `xlsxwriter` caps a sheet at 1,048,576 rows. Options: (a) ZIP of several XLS files of 1M rows each, (b) drop XLS for large datasets and tell customers to use CSV. Alex prefers (a). Asked Dana on 2026-10-06. Affects Acme (4.2M rows).
2. **Pool size.** 3 workers pass Acme's 15-minute SLA only when a single export runs. Three parallel exports take 21 minutes. 6 workers would fix it for about 1,200 USD per month extra. Needs a budget decision.
3. **Email template wording and logo.** Marketing has the draft since 2026-10-12.
4. **DBA window for migration 0042.** Ticket DBA-5521. Tuesdays and Thursdays 22:00-23:00 UTC. Someone has to book a slot and be reachable during it.
5. **Owner of 3 unmapped cron jobs** (`export_weekly_xls`, `export_audit`, `export_adhoc`). Nobody on the team knows. They must be mapped or retired before the old cron is switched off.
6. **Cutover date.** The target is Tuesday 2026-11-10, but the rollout (T9) cannot start until T4, T5, T6 and T7 are done. If the decisions slip past 2026-10-30 the date is at risk.

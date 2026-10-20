🟡 **Go with conditions - split the upgrade.** Upgrade 7 of 9 services before the 2026-11-01 freeze and defer `auth-service` and `user-store` to January. The seven pass staging and, per the Platform notes, roll back in 10-15 minutes; the two have no rollback and are failing or untested. Confidence: medium, staging evidence only.

**Decisions for Marcus**
- Plan, by Fri 2026-10-23 - recommend (suggested): the split, so the Data team can start Mon 2026-10-26.
- v8 extended support (18,000 USD per quarter), by Thu 2026-11-05 - recommend (suggested): order it, because v8 security support ends 2026-11-12 and two services stay on v8.

**Top risks**
- 🔴 Upgrading `auth-service` or `user-store` now: no rollback, and six services depend on `auth-service`.
- 🟠 v8 patches stop on 2026-11-12: unpatched, or 18,000 USD per quarter.
- 🟠 The notes don't say whether the seven were tested next to a v8 `auth-service`; worth asking Platform before Monday.

**Read** `outputs/report.md`: start at "START HERE" (one minute), then section 3 for the three options. The audit trail is `outputs/report.evidence.md` plus `outputs/report.data/`, byte-exact copies of your three files with their checksums.

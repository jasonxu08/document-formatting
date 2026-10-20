# Runtime upgrade (v8 to v10) - notes for the decision

Written by the Platform team, 2026-10-14. Decision owner: the Engineering Lead (Marcus Hale). Decision needed by Friday 2026-10-23.

## Context

- Runtime v8 reaches end of security support on 2026-11-12. After that date there are no CVE patches unless we buy extended support.
- Code freeze runs from 2026-11-01 to 2027-01-05. During the freeze only P1 hotfixes deploy. Anything else needs an exception from the change advisory board (CAB).
- The question: upgrade before the freeze, or defer everything to January?
- The nine services and who depends on whom are in `services.csv`. Last quarter's incidents are in `incidents-q3.csv`.

## What the upgrade changes (breaking changes that matter to us)

1. The JSON serializer defaults changed (property naming, null handling). The custom converters in connector-service and share-service must be re-tested. Staging shows both pass.
2. The default HTTP client handler and retry behaviour changed. gateway has a custom retry policy. Staging shows it passes.
3. Identity library: auth-service uses IdentityModel 5.x. The v10-compatible release (6.0) is announced by the vendor "by end of November" but not committed. Until then auth-service would run on a compatibility shim.
4. The database driver used by user-store changes the schema migration format. Migrations are one-way after the upgrade.

## Staging results (2026-10-09 to 2026-10-11)

- 7 of 9 services: all tests pass.
- auth-service: 2 of 148 integration tests fail (token refresh flow, running on the compatibility shim). Root cause not confirmed.
- user-store: not tested. There is no staging environment for it. Building one is about one week of work.

## Rollback

- The 7 passing services: redeploy the previous version, 10 to 15 minutes.
- auth-service and user-store: no rollback path after the schema migration. Recovery means restoring from backup, estimated RTO 4 hours.

## Costs and options

- Extended support for v8: 18,000 USD per quarter, security patches only. Must be ordered by 2026-11-05 to be active on 2026-11-12.
- A CAB exception for upgrading during the freeze is possible, but only for work that is already staged and tested.
- Team capacity: the Identity team has 2 engineers. One is on leave from 2026-10-26 to 2026-11-13.
- The Data team says it can upgrade its four services (catalog-service, share-service, map-service, search-index) in one week if it starts Monday 2026-10-26.

## Quotes from the teams

- Identity: "We would rather not touch auth-service until the vendor library is out. A failed upgrade takes down every login."
- Data: "We can do ours in a week if we start Monday."
- Platform: "gateway should go last among the ones that pass, because it fronts everything."
- Integration: "connector-service is low risk, we can go any time."

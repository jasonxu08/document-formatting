# Cold-read answers

Based only on `top.md` (first 60 lines) and its one image, `dependency-map.png`.

## 1. What it is about, and the main message
This is a draft decision report (dated 2026-10-19, written for Marcus Hale, Engineering Lead) on upgrading nine services from runtime v8 to v10 before a code freeze that runs 2026-11-01 to 2027-01-05; the runtime itself is not named in what I can see. Its message is "go with conditions": upgrade seven services before the freeze (they pass staging and roll back in 10-15 minutes) and defer `auth-service` and `user-store` to January (no rollback, failing or untested), with medium confidence because the evidence is staging only.

## 2. Decision or action requested
- Marcus Hale decides the plan by Fri 2026-10-23; the recommendation is the 7-now / 2-later split, so the Data team can start on Mon 2026-10-26.
- Marcus also decides on v8 extended support (18,000 USD per quarter; the approver is not named in the notes) by Thu 2026-11-05; the recommendation is to order it.
- The "conditions" behind "go with conditions" are not listed explicitly in the part I can see.

## 3. Most important risks, in the document's order (blast radius first)
1. Upgrading `auth-service` or `user-store` before January: no rollback (restore from backup takes about 4 hours); a failure "takes down every login".
2. v8 loses security patches on 2026-11-12: CVEs stay open unless extended support is bought (18,000 USD per quarter).
3. Seven v10 services running next to a v8 `auth-service`: not shown as tested, and defects would surface while only P1 hotfixes can deploy.
4. Data's one-week plan leaves no spare day before the freeze: a slip needs a change-board (CAB) exception or waits for January.
5. January depends on a vendor promise: the identity library IdentityModel 6.0 is expected "by end of November", not committed.

Caveat: it is a desk review of staging results; nothing was re-tested.

## 4. Key components and how they relate
- Nine services in two groups. Upgrade before the freeze (7): `gateway` (Platform, critical, upgraded last), `share-service` and `catalog-service` (Data, high), `connector-service` (Integration, medium), `notify-service` (Platform, low), `map-service` and `search-index` (Data, medium). Defer to January (2): `auth-service` (Identity, critical, 2 of 148 tests fail) and `user-store` (Identity, critical, never tested).
- The map (arrow = "depends on", 16 arrows from the inventory): `gateway` depends on `share-service`, `connector-service` and `catalog-service`; `share-service` and `connector-service` depend on `catalog-service`; `share-service` also depends on `notify-service`; `catalog-service` and `map-service` depend on each other; `catalog-service` depends on `search-index`. Six services (all of the seven except `search-index`) depend on `auth-service`, which depends on `user-store`, so those two have to wait together.
- Terms defined: freeze (only P1 hotfixes, otherwise a CAB exception), extended support (paid v8 security patches), compatibility shim (stop-gap to run `auth-service` on v10 until IdentityModel 6.0 ships). How the shim figures in the plan is not visible.

## 5. Numbers and dates that matter
- 7 of 9 services pass staging (staging run 2026-10-09 to 10-11); 2 are deferred.
- Dates: decide Fri 2026-10-23; Data starts Mon 2026-10-26; freeze 2026-11-01 to 2027-01-05; extended-support decision Thu 2026-11-05; v8 security patches end 2026-11-12 (11 days after the freeze starts).
- Money: 18,000 USD per quarter for extended support.
- Rollback: 10-15 minutes for the seven versus about 4 hours (restore from backup) for `auth-service`.
- `auth-service`: 6 dependents, 11 of 36 Q3 incident records, 2 of 148 tests failing (the 148 figure is from the map). Q3 = 2026-07-01 to 2026-09-30.
- Vendor library IdentityModel 6.0 "by end of November"; 16 dependency arrows on the map.

## 6. What I would read next
Section 3, "The split beats upgrading all nine or deferring all nine" - the document itself says "Only deciding? Read 3, then stop." I expect three options (upgrade all nine, the split, defer all nine) compared on risk, cost and timing, with the reasoning for the split and for buying extended support. After that I would read section 2 for the evidence on why `auth-service` and `user-store` wait (its hub role and the Q3 incidents).

Not visible to me: the other six rows of the per-service table in section 1 (the excerpt stops after `gateway`, `catalog-service` and `share-service`), the exact January date for the deferred services, and any detail of the three options.

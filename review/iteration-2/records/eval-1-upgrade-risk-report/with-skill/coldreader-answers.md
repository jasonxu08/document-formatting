1. A report on moving nine services from runtime v8 to v10 before a deployment freeze (2026-11-01 to 2027-01-05).
   Its message is "go with conditions": upgrade the seven services that passed staging from 2026-10-26 once a mixed-version check passes,
   and defer auth-service and user-store (the "Identity pair") to January because they have no rollback and are not ready;
   v8 extended support is needed either way.

2. Marcus Hale (Engineering Lead) is asked to decide three things:
   (1) approve the split plan - the seven from Mon 2026-10-26, Identity pair in January - by Fri 2026-10-23 (recommend: approve);
   (2) order v8 extended support (18,000 USD a quarter) by Thu 2026-11-05 (recommend: order);
   (3) request a change advisory board (CAB) exception by Fri 2026-10-23 (recommend: ask).

3. Ranked: (1) Identity pair upgraded before it is ready: no rollback, 4 h restore, every login down.
   (2) A slip or regression lands in the freeze: only P1 hotfixes deploy, so fixes need a CAB exception.
   (3) Identity pair on unpatched v8 after 2026-11-12: no CVE fixes for login unless support is ordered.
   (4) Vendor library 6.0 slips past November: shim stays, support renews at 18,000 USD/quarter. (5) Mixed v8/v10 estate not shown tested.

4. Nine services: the seven (gateway, catalog-service, share-service, connector-service, map-service, search-index, notify-service)
   passed staging and roll back in 10-15 min; the Identity pair (auth-service, user-store) has no rollback and is not ready.
   Six services depend on auth-service, which rests on user-store, so an Identity failure can reach seven of the other eight;
   catalog-service and map-service depend on each other. Plan: mixed-version check, then the seven, then the Identity pair in January.

5. Dates: plan and CAB decisions due Fri 2026-10-23; support decision Thu 2026-11-05; the seven start Mon 2026-10-26;
   freeze 2026-11-01 to 2027-01-05; v8 normal support ends 2026-11-12; staging was 2026-10-09 to 10-11; mid-December review.
   Numbers: 7 of 9 services ready; rollback 10-15 min (the seven) vs none (Identity pair); 4 h restore if Identity fails;
   6 services depend on auth-service; 2 of 148 auth-service tests fail; extended support 18,000 USD a quarter.

6. Section 5, "The seven fit before the freeze with no slack": the nearest decisions (due 2026-10-23) hinge on it, and the confidence note
   calls the seven's schedule the weakest part. I expect the upgrade order and dates against the 2026-11-01 freeze, the mixed-version
   check as a go/no-go, and why a CAB exception is needed (gateway, slips, rollbacks).

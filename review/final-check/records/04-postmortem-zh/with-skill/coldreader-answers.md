# Cold-reader answers (top.md + the 2 images it references)

## 1. What is it about, and the main message
A postmortem (dated 2026-10-19) of the 9 October (Friday) ordering/payment outage: config change CFG-2231 mistakenly cut the order service's connection-pool limit from 200 to 20 (meant for the test environment only) and was pushed to everything at once at 14:02 with no canary, so ordering and payment failed for 105 minutes (~3,800 failed orders, ~1,200 users) until the 15:10 rollback. The message: the incident is over and the root cause is solid, but none of the six follow-up improvements is prioritised yet (17 person-days of work vs ~10 available), so the same kind of misconfiguration can still happen; and 56 of the 105 minutes passed before anyone found the cause.

## 2. Decision / action requested
- **From Zhang Wei (张伟, tech lead):** choose which improvement items to do first in the next iteration (6 items = 17 person-days; only ~10 free). The report recommends A4 on-call runbook, A6 two-person review, A3 alert threshold, A1 value validation, A5 retry backoff (9 person-days together) and deferring A2 canary (8 person-days).
- **From Zhang Wei:** decide whether to add a new item, "per-environment default config values" (raised in the incident chat; none of the six covers it; no date, owner or effort known). The report suggests deciding it together with the first, after estimating the effort.
- **By when:** no calendar date is given. The source gave none; the report only suggests deciding "before the next iteration is scheduled".
- Also implied, with no owner or date visible: unnamed colleagues are to verify the Section 5 data (status line: "final, Section 5 data awaiting verification").
- Glitch: the line labelled "排错的代价" (literally "cost of troubleshooting") reads oddly. From its content (the same misconfiguration can still go out in full with no validation or canary; payment still amplifies any order-service failure) I take it to mean "the cost of not deciding".

## 3. Most important risks / problems (the report's own order; it says the ranking is its judgement)
1. Config changes can still go live to everyone with no validation and no canary, so one wrong value takes effect everywhere again.
2. Test-environment changes can still be written as global defaults, and no improvement item covers it, so the path that caused this incident is still open.
3. Payment still retries the order service with no backoff and no circuit breaker, so any slowness in orders drags payment down.
4. On-call still does not check config changes first: after the chat was opened it took 38 minutes to find the cause.
5. 6 items / 17 person-days against a ~10 person-day budget: if not ranked, the biggest item crowds out the rest.
- Data caveat: impact numbers are "medium" confidence (taken from the timeline, not checked against monitoring); four places where sources disagree and two things the source does not say are in Section 5, which is not visible to me.

## 4. Key things / steps and how they relate
- **Causal chain:** the wrong value in CFG-2231 (merged 13:58) goes via the config center to gateway, order-service and payment-service (14:02, all at once) -> order-service pool cap 200->20, requests queue, P99 slows -> gateway shows rising 5xx on order endpoints -> payment-service retries the order service with no backoff (retry storm, CPU 90%+), which loads the order service further. So order-service is the fault point and payment's retries are the amplifier.
- **System diagram:** arrows are calls (gateway -> order, user; order -> payment, inventory, user; payment -> notification; inventory, user -> cache); the config center's "push config" arrows are the exception. Red = fault point (order), orange = affected (gateway, payment), grey = not said to be affected (inventory, user, notification, cache). The red dashed payment->order "retry" link comes from the chat; the service list does not record it.
- **Timeline (6 phases, chart):** push->alert 7 min; alert->chat opened 11; chat->root cause found 38 (longest); root cause->rollback 12; rollback->latency recovered 15; recovered->declared over 22. The first three (red) are "cause unknown" = 56 min (53%); the last three = 49 min; rollback plus taking effect was only 27 min.
- **Improvement items:** A1 value validation, A2 canary, A3 alert threshold, A4 on-call runbook, A5 retry backoff, A6 two-person review (the A1-A6 table is in Section 4, not visible to me). The "per-environment defaults" idea would be an extra item.

## 5. Numbers and dates put in front of me
- **Duration:** 105 min outage; 56 min (53%) before the cause was found; 38 min the longest stretch (chat opened -> cause found); 49 min after; 27 min rollback plus effect. Segments: 7 / 11 / 38 / 12 / 15 / 22.
- **Impact:** ~3,800 failed orders, ~1,200 affected users (medium confidence). Pool limit 200 -> 20; payment CPU 90%+ (diagram).
- **Clock times (9 October, Friday, Beijing time):** 13:58 CFG-2231 merged; 14:02 full push; 14:58 cause found (labelled in the chart); 15:10 rollback. Other times are not printed; by arithmetic the outage ended around 15:47. The 105 min appears to run to "declared over", so it includes a 22-minute tail after latency recovered. I cannot tell from the top whether orders were still failing in that tail.
- **Decision numbers:** 6 items = 17 person-days vs ~10 available; recommended five = 9 person-days; A2 = 8 person-days (deferred).

## 6. What I would read next
Section 4 ("improvement-item ranking: do five first, 9 person-days; A2 deferred"). It is where the requested decision lives and where the top leaves gaps. I expect the table decoding A1-A6 (what each is, probably its person-days), the reasoning for the order (why A4/A6/A3/A1/A5 first and why the 8-day canary is deferred), the arithmetic against the ~10 person-day budget, and probably what risk stays open while A2 waits. After that, Section 3 for the second decision: I expect a walk through seven lines of defence showing why none stopped the wrong config. Section 2 (minute-by-minute story) would come only if I wanted the narrative first.

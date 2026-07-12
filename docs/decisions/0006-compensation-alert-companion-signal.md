# 0006 — Non-compensatory companion signal (max_component + compensation_alert)

- **Status**: deferred
- **Cycle**: 1
- **Proposer**: stat-methodologist
- **Component**: composite

## Context

The linear composite implies full compensability: a critical-band component is averaged away (fixture BCS: cpr 0.816 'critical band' inside SI 0.4207 'moderate'; synthetic cpr=1.0 case reads 'low' at 0.2400). Nothing in score_dataframe or aggregate_contract surfaces the masking. OECD Handbook §6.11 (E1, verbatim) documents full compensability as the known defect of additive aggregation.

## Proposal (rebuttal-revised)

Append `max_component = max(ccs, eav, cpr)` — hazard components only, UNCONDITIONALLY (the skeptic proved the original wm-inclusive spec fires on zero-hazard weight-4/5 measures) — and `compensation_alert = (max_component >= RISK_TIERS['critical'][0]) & (shock_index < RISK_TIERS['high'][0])`, dtype bool; add `n_compensation_alerts` to aggregate_contract; E4 label for threshold reuse; fixture-prevalence and cpr(guardrail)=1−L coupling documented; corrected citation Greco, Ishizaka, **Tasiou** & Torrisi (2019) and the same fix to the methodologist charter file.

## Decisive critique and verdict

**Defer.** The rebuttal repaired the real defects, but two dependencies point at next cycle: (1) the accepted ADRs 0002/0003 change the fixture truth table this proposal's oracles pin (BCS's alert flips to False because its composite now reads 'high' 0.502767 — the alert set shrinks exactly where masking was removed, which is evidence the signal works, but the oracles must be re-derived against the accepted composite); (2) robustness of the alert set is coupled to `_CPR_LATENT_SHARE` (discontinuity at L = 0.25), which is only perturbable once CAL-2 (also deferred) lands. Re-enters next cycle bundled with CAL-2, with oracles derived from the post-batch formula text. Cap note: this cycle's four slots went to the two formula corrections it depends on plus the two hardening items that pin them.

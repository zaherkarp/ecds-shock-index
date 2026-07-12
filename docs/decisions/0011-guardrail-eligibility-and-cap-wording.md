# 0011 — Guardrail cap form and eligibility misstated (year-3 inversion; ±5% shorthand)

- **Status**: deferred
- **Cycle**: 1
- **Proposer**: stat-domain-evidence
- **Component**: cpr

## Context

The repo states the guardrail as '±5% for non-CAHPS measures with at least three years of data'. Per the 2026 Technical Notes (E1, fetched and pdftotext-verified by three roles): the cap is 5 **percentage points** (0–100 scale) or 5% of the prior year's restricted score range; guardrails are NOT applied to improvement measures or measures in the program **3 years or less** (respecified measures treated as new). The repo's wording inverts the year-3 case in three locations, and the ±5% shorthand appears in seven more (programmer's grep, reproduced by the proposer, including the user-visible `--guardrail` help string and two agent charter files). guardrail=0.05 itself remains numerically correct for 0–100-scale rates in fraction units; cpr_score(0.02) = 0.32 unchanged.

## Proposal (rebuttal-revised)

Ten-location documentation-only fix with tiering (three outright inversions vs seven imprecise shorthands), percent-sign-free CLI help text (removes the argparse %%-escaping hazard), and the canonical long-form correction. Functional-form implication (guardrail-exempt CPR mode — for an exempt measure at shift 0.15 the current form gives 0.84 vs 0.30 uncapped, a 0.54 component discrepancy) handed to stat-methodologist.

## Decisive critique and verdict

**Defer** — cap-forced only; unanimous support and 6/6 verbatim quote-checks. Referee sign-off for the two charter-file edits (locations 9 and 10) is **granted here**, so next cycle lands the full ten-location list without re-litigation. The exempt-mode formula proposal is expected from stat-methodologist with CAL-2 (0008) as its parameter surface. Regrade carried E1 citations E2-cached if not re-fetched next cycle.

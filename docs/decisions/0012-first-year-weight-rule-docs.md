# 0012 — Document the first-year weight-1 rule for new measures (wm_score docstring, README weights row)

- **Status**: deferred
- **Cycle**: 1
- **Proposer**: stat-domain-evidence
- **Component**: wm

## Context

The wm_score docstring and README omit a rule CMS applies every year (E1, verbatim, three independent fetches): new measures carry weight 1 in their first year; the category weight applies thereafter. Live in 2026: respecified Improving/Maintaining Physical/Mental Health measures are Intermediate Outcome Measures at '1*' (Table G-1 + footnote confirming return to weight 3 for 2027 — the skeptic's stronger corroboration). A user assigning category weight 3 to a first-year outcome measure overstated the old composite by exactly 0.20·(0.6−0.2) = 0.08. The skeptic correctly demoted the Kidney Health (C13) corroboration: it is a Process Measure whose category weight is 1 anyway — only C04/C05 are demonstrative.

## Proposal

Append the first-year rule to the wm_score docstring; README weights row becomes '1, 2, 3, or 5; new measures are weighted 1 in their first year' (also fixing the nonexistent weight-4 implication of '1–5'). No formula change; max_weight = 5.0 stays correct.

## Decisive critique and verdict

**Defer** — cap-forced only; unanimous support. Binding rewording condition for next cycle: with ADR 0002 accepted, the impact mechanism is no longer '+0.08 on the composite' — the wrong input now distorts **contract aggregation shares** (weight 3 vs 1 changes a measure's share, e.g. 3/5 vs 1/3 of total weight on the fixture), exactly the conditional framing calibration and the skeptic required. Lean evidentially on C04/C05 only. Regrade carried citations E2-cached if not re-fetched.

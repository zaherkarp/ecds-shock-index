# 0011 — Guardrail cap form and eligibility wording (year-3 inversion plus percent-shorthand) — 11 locations

- **Status**: accepted
- **Cycle**: 2 (deferred cycle 1, accepted cycle 2)
- **Proposer**: stat-domain-evidence
- **Component**: cpr

## Context

The repo states the guardrail as '+-5% for non-CAHPS measures with at least three years of data'. Both halves are wrong per the 2026 Technical Notes, re-fetched and quote-verified this cycle: (1) the cap is 5 PERCENTAGE POINTS on a 0-100 scale or 5% of the prior year's restricted score range — not a relative +-5%; (2) eligibility is INVERTED: guardrails are NOT applied to improvement measures or to measures in the program 3 years or less (respecified measures treated as new), so a measure with exactly 3 years is exempt, the opposite of 'at least three years'. 11 live locations identified (superseding cycle-1's count of 10; the notebook markdown cell is the 11th).

## Proposal

Documentation-only, 11 locations. 3 inversions (cpr_score docstring at `__init__.py`, `literature-evaluation.md` Program context, `stat-domain-evidence.md` charter) and 8 shorthands (cli.py help, README.md ×2, `literature-evaluation.md` ×2, blog, notebook cell, `stat-methodologist.md`). Canonical long form applied per-location. `guardrail=0.05` stays numerically correct (5 pp on 0-100 scale = 0.05 in fraction units); no code, oracle, or default change.

## Evidence

| Claim | Grade | Source | URL | Accessed | Supporting quote |
|---|---|---|---|---|---|
| The guardrail cap is 5 pp (0-100 scale) or 5% of prior-year restricted range | E1 | CMS 2026 Star Ratings Technical Notes | https://www.cms.gov/files/document/2026-star-ratings-technical-notes.pdf | 2026-07-13 | 'capped at an increase or decrease of at most 5 percentage points for measures having a 0 to 100 scale (absolute percentage cap) or at most 5 percent of the prior year's restricted score range' |
| Guardrails NOT applied to improvement measures or measures in program 3 years or less; respecified treated as new | E1 | CMS 2026 Star Ratings Technical Notes, p. 147 | https://www.cms.gov/files/document/2026-star-ratings-technical-notes.pdf | 2026-07-13 | 'Guardrails are not applied to the Part C and Part D improvement measures. Additionally, guardrails are not applied to new measures that have been in the Part C and D Star Rating program for 3 years or less.' |
| Behavior-invariant: cpr(0.02)=0.32, cpr(0.05)=0.80 unchanged | E3 | In-repo computation | | 2026-07-13 | guardrail=0.05 stays the correct fraction-unit encoding |

## Numerical verification

| Inputs | Old output | New output | Derivation |
|---|---|---|---|
| cutpoint_shift=0.02, guardrail=0.05 | cpr=0.32 | cpr=0.32 | 0.80*min(0.02,0.05)/0.05 + 0.20*max(0,0)/0.5 = 0.32 (unchanged) |
| cutpoint_shift=0.05, guardrail=0.05 | cpr=0.80 | cpr=0.80 | 0.80*1.0 + 0.20*0 = 0.80 (unchanged) |
| contract weighted index | 0.3057 | 0.3057 | Doc-only change, golden file untouched |

## Verdict

Accepted. Both CMS Technical Notes E1 quotes verified verbatim by all five critics. 11 locations confirmed. Behavior-invariant.

## QA result

Pending (cycle-2 QA gate).

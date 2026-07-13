# 0008 — Expose CPR latent share as a validated public parameter

- **Status**: accepted
- **Cycle**: 2 (resubmitted from cycle 1 deferral)
- **Proposer**: stat-calibration
- **Component**: cpr

## Context

`_CPR_LATENT_SHARE = 0.20` was a module-private E4 judgment controlling the
realized/latent split in `cpr_score`. At the guardrail boundary, `cpr = 1 − L`
identically, so the parameter spans cpr values [0.0, 1.0] over L in [0, 1] — yet it
could not be varied through any public path. This blocked uncertainty propagation per
OECD/JRC Handbook §1.7 and made sensitivity analysis (ADR-0007) incomplete.

## Proposal

1. Rename `_CPR_LATENT_SHARE` → `CPR_LATENT_SHARE_DEFAULT = 0.20` (public constant,
   E4-labeled docstring including degenerate L = 1.0 boundary).
2. Add `latent_share` keyword to `cpr_score(cutpoint_shift, guardrail=0.05,
   max_shift=0.5, latent_share=CPR_LATENT_SHARE_DEFAULT)` with `_require_finite`
   validation and `0.0 <= latent_share <= 1.0` bounds check.
3. Thread `latent_share` through `score_dataframe()` and `--latent-share` on the CLI
   batch subparser (default references the constant).
4. Add `CPR_LATENT_SHARE_DEFAULT` to `__all__`.
5. Document the L = 1.0 degenerate boundary: realized term vanishes, so a shift exactly
   at the guardrail scores 0.0.

## Evidence

| Claim | Grade | Source | URL | Accessed | Supporting quote |
|---|---|---|---|---|---|
| Composite indicators must expose tunable parameters for sensitivity analysis | E1 | OECD/JRC Handbook on Constructing Composite Indicators, §1.7 | https://www.oecd.org/en/publications/handbook-on-constructing-composite-indicators-methodology-and-user-guide_9789264043466-en.html | 2026-07-13 | "Uncertainty and sensitivity analysis should be undertaken to assess the robustness of the composite indicator… in terms of the mechanism for including or excluding indicators, the… weights" |
| L = 0.20 is an E4 judgment; exposure as a kwarg does not change its value | E4 | In-repo expert judgment (cycle 1 debate) | — | — | — |
| Degenerate L = 1.0: realized term vanishes, shift at guardrail → 0.0 | E3 | In-repo derivation | — | — | CPR = (1−1)·1.0 + 1·0.0 = 0.0 |

## Critiques

| Critic | Stance | Summary |
|---|---|---|
| stat-skeptic | support | Attacked and could not break it in cycle 1. L = 1.0 boundary is correctly documented. |
| stat-methodologist | support | Parameter exposure is a prerequisite for proper sensitivity analysis; functional form unchanged. |

## Rebuttal

No opposition. Degenerate L = 1.0 boundary documentation added per skeptic's standing
condition from cycle 1.

## Verdict

**Accept.** The parameter was already implemented and defended in cycle 1; deferral was
cap-forced, not merit-based. Exposure as a validated keyword with documented boundaries
is a methodological prerequisite for ADR-0007 sensitivity tooling. No formula change,
no oracle regression.

## Numerical verification

Worked from the accepted formula `CPR = (1−L)·min(|shift|,g)/g + L·max(|shift|−g,0)/m`:

| Inputs | Old output | New output | Derivation |
|---|---|---|---|
| shift=0.02, g=0.05, m=0.5, L=0.20 | 0.32 | 0.32 (unchanged) | (0.80)(0.4) + (0.20)(0) = 0.32 |
| shift=0.09, g=0.05, m=0.5, L=0.50 | n/a (not exposable) | 0.54 | (0.50)(1.0) + (0.50)(0.08) = 0.54 |
| shift=0.05, g=0.05, m=0.5, L=1.00 | n/a (not exposable) | 0.00 | (0.00)(1.0) + (1.00)(0.0) = 0.0 |
| BCS row, L=0.50, default weights | n/a | SI=0.4338 moderate | ccs=0.30, eav=0.5361, cpr=0.54; 0.4375(0.30)+0.3125(0.5361)+0.25(0.54)=0.4338 |

## Implementation

Files changed:
- `src/ecds_shock_index/__init__.py`: renamed constant, added `latent_share` kwarg to
  `cpr_score` and `score_dataframe`, added `CPR_LATENT_SHARE_DEFAULT` to `__all__`
- `src/cli.py`: added `--latent-share` flag, imported `CPR_LATENT_SHARE_DEFAULT`,
  threaded to `score_dataframe`
- `docs/literature-evaluation.md`: CPR section updated to reference public constant
  and ADR-0008

Tests added:
- `test_cpr_score_latent_share_default`: cpr(0.02, L=0.20) = 0.32
- `test_cpr_score_latent_share_half`: cpr(0.09, L=0.50) = 0.54
- `test_cpr_score_latent_share_degenerate`: cpr(0.05, L=1.0) = 0.0
- `test_cpr_score_latent_share_validation`: L=-0.1 and L=1.5 raise ValueError
- `test_score_dataframe_latent_share_threading`: BCS cpr=0.54, SI=0.4338, tier=moderate

Golden file unchanged: default L=0.20 produces identical values.

## QA result

Pending cycle-2 QA gate.

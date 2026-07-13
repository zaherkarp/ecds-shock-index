# 0007 — Weight sensitivity tooling (OAT + simplex) and E4 labeling of composite weights

- **Status**: accepted
- **Cycle**: 2 (resubmitted from cycle 1 deferral)
- **Proposer**: stat-calibration
- **Component**: composite

## Context

The composite weights (0.4375, 0.3125, 0.25) are asserted without calibration evidence
and the repo had no sensitivity tooling — the exact OECD/JRC Handbook step-7 gap. The
BCS measure straddles the high/moderate boundary at SI = 0.5028 (margin 0.0028), making
it the most fragile measure under weight perturbation.

## Proposal

1. New module `src/ecds_shock_index/sensitivity.py` exporting `weight_sensitivity(scored_df,
   calculator=None, deltas=(0.05, 0.10, 0.20), include_zero_weights=False)` returning a
   tidy long DataFrame with columns: weight_name, signed_delta, l1_radius, alpha_ccs,
   beta_eav, gamma_cpr, measure_id, shock_index_before, shock_index_after, tier_before,
   tier_after, tier_flip, validity_domain_r.

2. New script `scripts/weight_sensitivity_analysis.py` with OAT and uniform-Dirichlet(1,1,1)
   samplers (stdlib random, seed 7, N=200000) for reproducible analysis.

3. Zero-default weights (delta_wm under ADR-0002) excluded by default unless
   `include_zero_weights=True`.

4. Validity domain radius `2·min(w_perturbed, min(others))` reported per perturbation to
   flag when an OAT step exits the feasible simplex neighborhood.

## Evidence

| Claim | Grade | Source | URL | Accessed | Supporting quote |
|---|---|---|---|---|---|
| Step 7: uncertainty and sensitivity analysis must assess robustness of composite weights | E1 | OECD/JRC Handbook on Constructing Composite Indicators, §1.7 | https://www.oecd.org/en/publications/handbook-on-constructing-composite-indicators-methodology-and-user-guide_9789264043466-en.html | 2026-07-13 | "Uncertainty and sensitivity analysis should be undertaken to assess the robustness of the composite indicator… in terms of the mechanism for including or excluding indicators, the… weights" |
| BCS SI = 0.5028 straddles high/moderate at margin 0.0028 | E3 | In-repo fixture derivation (ADR-0005) | — | — | 0.4375(0.30) + 0.3125(0.5361) + 0.25(0.816) = 0.5028 |
| OAT alpha+0.05 flips BCS to moderate (SI = 0.4847) | E3 | In-repo derivation | — | — | (0.4875)(0.30) + (0.2847)(0.5361) + (0.2278)(0.816) = 0.4847 |
| Critical L1 radius for BCS flip = 0.01535 | E3 | In-repo derivation | — | — | d_crit = (0.50 − 0.5028)/(0.30 − 0.6605) = 0.00767; L1 = 2d = 0.01535 |

## Critiques

| Critic | Stance | Summary |
|---|---|---|
| stat-skeptic | support | Re-derived OAT oracle independently; confirmed BCS flip at delta=0.05 and straddle at L1 ~ 0.01535; acceptance rate for L1 ≤ 0.10 ball is ~0.27%. |
| stat-methodologist | support | Tooling addresses the OECD step-7 gap; OAT + Dirichlet covers both local and global sensitivity. |

## Rebuttal

No opposition. All tables regenerated on the 3-hazard-weight simplex under accepted
weights (0.4375, 0.3125, 0.25) per cycle-1 deferral condition.

## Verdict

**Accept.** The tooling is a prerequisite for defensible weight claims. OAT confirms
local robustness (zero flips at L1 ≤ 0.01534) while exposing the BCS fragility
(flip at L1 = 0.01535). The Dirichlet sampler provides global coverage. No formula
or oracle change to existing components.

## Numerical verification

| Inputs | Output | Derivation |
|---|---|---|
| BCS, alpha+0.05 renormalized | SI = 0.4847, tier = moderate, flip = True | a=0.4875, b=0.5125×0.3125/0.5625=0.2847, g=0.5125×0.25/0.5625=0.2278; SI=0.4875(0.30)+0.2847(0.5361)+0.2278(0.816)=0.4847 |
| BCS, alpha+0.00767 | SI ≈ 0.5000, no flip (stays high) | d=0.00767, L1=0.01534; SI=0.5028+0.00767(0.30−0.6605)=0.5000 |
| BCS, alpha+0.00768 | SI < 0.5000, flip to moderate | d=0.00768, L1=0.01536; SI=0.5028+0.00768(0.30−0.6605)=0.4999 |
| BCS validity_domain_r | 0.50 | 2·min(0.4375, 0.25) = 0.50 |

## Implementation

Files created:
- `src/ecds_shock_index/sensitivity.py`: `weight_sensitivity()` function
- `scripts/weight_sensitivity_analysis.py`: OAT + Dirichlet analysis script
- `tests/test_sensitivity.py`: 5 tests with hand-derived oracles

Tests:
- `test_default_weights_identity`: delta=0 returns unchanged SI, no flips
- `test_oat_bcs_flip`: alpha+0.05 → BCS SI=0.4847, tier flip high→moderate
- `test_bcs_straddle_oracle`: delta=0.00767 no flip, delta=0.00768 flip
- `test_validity_domain_r`: BCS validity_domain_r = 0.50
- `test_zero_weights_excluded`: delta_wm absent when include_zero_weights=False

Golden file unchanged: new module only, no existing formula/value changes.

## QA result

Pending cycle-2 QA gate.

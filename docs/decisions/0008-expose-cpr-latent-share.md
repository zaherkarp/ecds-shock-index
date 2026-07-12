# 0008 — Expose _CPR_LATENT_SHARE as a validated public cpr_score/score_dataframe/CLI parameter

- **Status**: deferred
- **Cycle**: 1
- **Proposer**: stat-calibration
- **Component**: cpr

## Context

`_CPR_LATENT_SHARE = 0.20` is a module-private E4 judgment that is also the most influential shape parameter of cpr_score (at the guardrail, cpr = 1 − L identically, spanning [0.5, 1.0] over plausible L), yet it cannot be varied through any public path — a structural block on the uncertainty propagation OECD §1.7 (E1, verbatim) requires. The full L-sweep was re-derived analytically by three roles: contract slope −0.1728 per unit L, moderate→low crossing at L = 0.6166, A1C at 0.7113, defaults bit-identical at L = 0.20.

## Proposal

Public `CPR_LATENT_SHARE_DEFAULT = 0.20` (E4-labeled), `latent_share` keyword on cpr_score with [0,1] validation, threaded through score_dataframe and `--latent-share` on the CLI batch subparser; E4 label + E3 sweep recorded in docs. Programmer notes accepted: CLI default references the constant; one batch-threading oracle; docs line 63 rename. Skeptic note accepted: document the degenerate L = 1.0 boundary (a shift at the guardrail scores 0.0).

## Decisive critique and verdict

**Defer** — cap-forced only; no critic opposed and the skeptic 'attacked and could not break it'. Priority next cycle: it is the parameter surface required by deferred 0006 (alert-set robustness, discontinuity at L = 0.25) and by the guardrail-exempt CPR mode handed to the methodologist in 0011's evidence. All doc-table composite/contract numbers must be recomputed under the accepted gamma_cpr = 0.25 composite (the component-level identity cpr = 1 − L is unaffected).

# 0007 — Weight sensitivity tooling (OAT + simplex) and E4 labeling of composite weights

- **Status**: deferred
- **Cycle**: 1
- **Proposer**: stat-calibration
- **Component**: composite

## Context

The composite weights are asserted without calibration evidence and the repo has no sensitivity tooling — the exact OECD checklist step-7 gap. The cycle's analysis (verified by three independent reproductions, including a different-seed Monte Carlo and an analytic proof) shows the old defaults were globally decisive (A1C tier differs in ~40% of simplex weight vectors) but locally robust (zero flips/reversals at L1 ≤ 0.10 — proven via the bound |ΔSI| ≤ (||Δw||₁/2)·range, adopted in rebuttal as the normative statement). The rebuttal resolved the one factual dispute: the '539 in-ball vectors' came from rejection sampling over 200,000 stdlib-random draws (seed 7), not the misdescribed n=20000/seed=42 scheme — re-executed, kept=539, 0 flips, consistent with the critics' ~0.27% acceptance rate.

## Proposal (rebuttal-revised)

`weight_sensitivity(scored_df, calculator=None, deltas=(0.05, 0.10, 0.20), include_zero_weights=False)` returning a tidy long DataFrame (typed columns; zero-default weights skipped unless flagged as inclusion/exclusion probes — the policy that defines behavior under ADR 0002's delta_wm=0); committed scripts/weight_sensitivity_analysis.py with samplers recorded verbatim; docs tables labeled worst-case envelopes; unit tests passing explicit deltas (0.255, 0.19, 0.20 radii unreachable on the default grid).

## Decisive critique and verdict

**Defer** — sequencing economics, not merit. Calibration itself established that every published table (flip radii, simplex frequencies) was computed on the 4-weight simplex and is stale the moment ADR 0002 lands; merging this cycle would mean recomputing all tables mid-batch. ADR 0002's E4-weight floor is satisfied by its embedded analytic 3-weight sensitivity disclosure. **First agenda item next cycle**: land the rebuttal-revised tooling against the pinned post-batch baseline, regenerate all tables over the 3-hazard-weight simplex under (0.4375, 0.3125, 0.25), and address the BCS 0.002767 margin fragility ADR 0002 discloses.

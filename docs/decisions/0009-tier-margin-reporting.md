# 0009 — Report tier robustness: tier_margin column in score_dataframe and key in aggregate_contract

- **Status**: deferred
- **Cycle**: 1
- **Proposer**: stat-calibration
- **Component**: tiers

## Context

The index reports hard tier labels with no fragility signal: two 'moderate' labels can carry order-of-magnitude different distance to a flip. This cycle's accepted batch sharpens the need: post-batch, BCS's 'high' label sits 0.002767 from the boundary — exactly what this column would expose.

## Proposal (rebuttal-revised)

`tier_margin(score)` = min distance to the interior tier boundaries, with boundaries derived once from RISK_TIERS (note: actual structure is dict[str, tuple(lo, hi)], so derive from RISK_TIERS.values(), not a 3-tuple unpack); appended CSV column and JSON key with ADR migration note; test_summary_keys six-key update (the proposal's 'nothing breaks' claim failed this exact-equality test — programmer's patched-copy run, conceded); unrounded-weighted pin; boundary oracles; docs framing as a deterministic distance conditional on an E4 tier scheme — explicitly NOT an uncertainty bound (skeptic's citation-stretch amendment, conceded) — read only alongside 0007's flip radii.

## Decisive critique and verdict

**Defer** — cap-forced, plus every published margin example is formula-dependent and must be re-derived against the accepted composite (BCS 0.0793 → 0.002767; contract 0.0720 → 0.055688; COL → 0.130424; A1C → 0.052032). Natural bundle with 0007 next cycle: margin (how far to a flip) + flip radii (what parameter movement produces it) is the coherent robustness report.

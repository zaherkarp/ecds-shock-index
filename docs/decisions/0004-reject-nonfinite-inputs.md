# 0004 — Refuse non-finite inputs at the scoring boundary (NaN silently scores maximum risk; inf scores sign-dependent extremes)

- **Status**: accepted
- **Cycle**: 1
- **Proposer**: stat-programmer
- **Component**: composite

## Context

`_clip_01(value) = max(0.0, min(1.0, value))` maps NaN to 1.0 by Python argument ordering (`nan < 1.0` is False, so `min(1.0, nan)` returns 1.0). Every scorer therefore silently scores NaN as MAXIMUM risk. The realistic trigger is in-repo: `merge_ecds_and_weights` uses `how='left'` (src/ecds_shock_index/data_loader.py:58), so an ECDS measure_id absent from the weights file gets NaN measure_weight → wm = 1.0 → a fabricated shock_index and tier — and is then silently EXCLUDED from `weighted_shock_index` (pandas skipna) while counted in `measure_count` and included in mean/max: an internally inconsistent summary. Domain evidence establishes measure-set churn as the expected annual operating condition, not an edge case. Rebuttal added the inf sub-finding: `ccs_score(inf, 0.9) = 0.0` and `wm_score(-inf) = 0.0` silently score MINIMUM risk, and `ccs_score(inf, -inf)` regenerates NaN internally (inf−inf) and clips to 1.0 — so a NaN-only guard is insufficient.

## Proposal

(1) Each public scorer raises ValueError on any non-finite float argument (`math.isfinite`). (2) `score_dataframe` pre-validates the five required columns for NaN and raises naming the offending measure_ids and columns. (3) `aggregate_contract` raises if shock_index or measure_weight contains NaN, so weighted/mean/max/count always describe the same rows. Left join in data_loader unchanged (loaders may surface unmatched rows for inspection; scorers must never launder them into [0,1]). **Breaking: true** (raises where output was previously returned) with migration note: complete the weights file or `df.dropna(subset=['measure_weight'])` before scoring; `test_left_join_preserves_unmatched` remains valid.

## Evidence

| Claim | Grade | Source | URL | Accessed | Supporting quote |
|---|---|---|---|---|---|
| All four scorers map NaN → 1.0 via argument order | E3 | In-repo reproduction (proposer + 3 independent reproductions) | — | 2026-07-11 | "min(1.0,nan)=1.0, min(nan,1.0)=nan; scorers on NaN: 1.0 1.0 1.0 1.0" |
| Unmatched merge → fabricated tier + inconsistent aggregate | E3 | In-repo end-to-end reproduction, 3 independent rebuilds | — | 2026-07-11 | "XYZ wm=1.0 shock_index=0.43225 'moderate'; aggregate {weighted 0.1325, mean 0.2824, max 0.4323, count 2, tier 'low'}" |
| inf lanes: silent minimum risk + internal NaN regeneration | E3 | Rebuttal reproduction runs | — | 2026-07-11 | "ccs_score(inf,0.9)=0.0; wm_score(-inf)=0.0; ccs_score(inf,-inf): raw=nan → 1.0" |
| Implicit imputation of missing data violates the composite-construction discipline | E1 | OECD/JRC Handbook (2008), robustness checklist | https://knowledge4policy.ec.europa.eu/sites/default/files/jrc47008_handbook_final.pdf | 2026-07-11 | "...the imputation of missing data, the choice of weights and the aggregation method." |

## Critiques

| Critic | Stance | Summary |
|---|---|---|
| stat-methodologist | support | Undisclosed worst-case imputation; the contract summary is statistically incoherent (statistics disagree about the sample). Fully reproduced. |
| stat-calibration | support | NaN-derived components are pinned at 1.0 under every weight vector — the most misleading failure mode for robustness reporting. Fully reproduced. |
| stat-domain-evidence | support | Measure churn is an annual regulatory reality (E1); stale weights files are the expected operating condition. Fully reproduced. |
| stat-skeptic | amend | (1) 'breaking: false' mislabeled — raises where a supported pipeline previously returned; (2) inf rejection was smuggled under NaN-only evidence (cpr/eav(inf) saturate defensibly). |

## Rebuttal

Both amendments conceded: breaking flag flipped to true with migration note; inf argued as its own sub-finding with new E3 (the silent-minimum lanes and the internal inf−inf → NaN lane, which defeats a NaN-only boundary check). Single invariant: no non-finite input may map into [0,1].

## Verdict

**Accept.** Decisive evidence: the three-way independently rebuilt end-to-end reproduction of the fabricated-tier/inconsistent-aggregate chain, plus the rebuttal's inf lanes closing the skeptic's over-reach objection with evidence rather than assertion. Conditions: ships breaking-with-migration; ADR presents NaN and inf sub-findings separately; TestNonFiniteInputs parametrized over nan/+inf/−inf including ccs_score(inf,0.9), wm_score(−inf), ccs_score(inf,−inf); sequenced first in the batch (independent, upstream). No new dependencies.

## Numerical verification

| Inputs | Old output | New output | Derivation |
|---|---|---|---|
| ccs/eav/cpr/wm on NaN | 1.0 (silent max risk) | ValueError | min(1.0, nan) = 1.0 by argument order — eliminated |
| ccs_score(inf, 0.9); wm_score(−inf) | 0.0; 0.0 (silent min risk) | ValueError | 1−(inf+0.9)/2 = −inf → clip 0.0; −inf/5 → clip 0.0 |
| ccs_score(inf, −inf) | 1.0 | ValueError | inf + (−inf) = nan → clip 1.0 (internal NaN regeneration) |
| Merge with XYZ unmatched → score_dataframe | XYZ wm=1.0, SI 0.43225 'moderate'; aggregate weighted 0.1325 over COL alone, count 2, tier 'low' | ValueError naming ['XYZ'] | SI = 0.35·0.135+0.25·0.10+0.20·0.8+0.20·1.0 = 0.43225 |
| Fixture (finite) | unchanged | unchanged | no NaN present; bit-identical at this step |

## Implementation

Files: src/ecds_shock_index/__init__.py (isfinite guards, score_dataframe/aggregate_contract validation), tests/test_core.py::TestNonFiniteInputs, tests/test_batch.py::test_unmatched_measure_id_raises, tests/test_batch.py::test_aggregate_contract_rejects_nan_weight. data_loader.py unchanged.

## QA result

**Pass** (gate 2026-07-12, zero blocking findings). Skeptic independently confirmed the
argument-ordering artifact (min(1.0, nan)=1.0 vs min(nan, 1.0)=nan), all three inf lanes
(0.0, 0.0, 1.0), and the fabricated-XYZ chain (SI 0.43225 'moderate', inconsistent mean
0.2824) against the old code via git show. Column-level behavior diff confirms the
finite-input path is bit-identical (ccs/cpr/wm columns unchanged vs baseline). JRC
robustness-checklist quote re-fetched verbatim 2026-07-12. TestNonFiniteInputs covers the
exact parametrization and three named lanes from the verdict conditions.

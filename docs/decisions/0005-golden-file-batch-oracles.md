# 0005 — Freeze a formula-derived golden file for the batch pipeline (currently zero numerical oracles)

- **Status**: accepted
- **Cycle**: 1
- **Proposer**: stat-programmer
- **Component**: repro

## Context

tests/test_batch.py asserts only structure/bounds and tests/test_cli.py only substrings; the sole numeric batch assertion is the degenerate zero-weight case. Mutation experiment (independently re-executed by two roles): multiplying every batch shock_index by 0.9 passes all 60 tests. The entire CSV → merge → score → aggregate path can silently drift — pandas major-version changes, wrong forwarded defaults, weight edits — undetected.

## Proposal

Add tests/golden/example_scored_golden.csv freezing the scored output of data/raw/example_ncqa_ecds.csv + example_cms_measure_weights.csv, with values hand-derived from the ACCEPTED formula text (ADRs 0002 + 0003), never from running the new code, and tests/test_golden.py::test_score_dataframe_matches_golden (pandas.testing.assert_frame_equal, atol=1e-9, rtol=0, full schema, no check_like, pinned column order) plus ::test_aggregate_contract_matches_golden. Binding clauses from the rebuttal: (a) sequencing — the golden is authored LAST in the batch from post-verdict formula text; (b) strictness — no column subsetting; any future schema-changing ADR regenerates the golden with hand-derived values for appended columns, so every output column always carries a value oracle.

## Evidence

| Claim | Grade | Source | URL | Accessed | Supporting quote |
|---|---|---|---|---|---|
| 10% corruption of batch shock_index passes all 60 tests | E3 | Mutation experiment, executed by proposer and independently re-executed by two critics (sed-inject, pytest, clean git revert, pytest) | — | 2026-07-11 | "60 passed in 2.47s ... after revert: 60 passed" |
| Golden values hand-derive from formula text and match execution | E3 | Independent hand derivations by three roles (current formula) + referee re-derivation (combined accepted formula) | — | 2026-07-11 | Combined table below; current-formula check: BCS 0.35·0.300+0.25·0.45+0.20·0.816+0.20·0.2 = 0.42070 |
| No numeric batch oracle exists today | E3 | grep of tests/ (verified by referee read of test_batch.py) | — | 2026-07-11 | only structural asserts + `weighted_shock_index == 0.0` degenerate case |

## Critiques

| Critic | Stance | Summary |
|---|---|---|
| stat-methodologist (reviewing) | amend | Golden must be derived from post-verdict formula text and sequenced last — otherwise stale on arrival (METH-1: BCS 0.475875; +METH-3: 0.50277 'high'). |
| stat-calibration | support | Independently re-ran the mutation; golden anchors the baseline for all sensitivity reporting; sequencing amendment endorsed. |
| stat-domain-evidence | support | Golden also freezes domain facts (fixture weights match real CMS categories); must be authored inside the batch ADR from the accepted formula set. |
| stat-skeptic | support | Verified blindness by exhaustive assertion inspection (charter bars file edits); all golden values re-derived by hand; tolerance sound; pin column order. |

## Rebuttal

Sequencing clause adopted verbatim as binding; strictness position taken (full-schema equality, regenerate per ADR) so appended columns can never ship without value oracles.

## Verdict

**Accept.** Decisive evidence: the twice-independently-re-executed mutation experiment proving total suite blindness on the showcased pipeline. Since ADRs 0002/0003 are accepted this cycle, the frozen values are the combined-formula table below (the proposal's current-formula values were explicitly illustrative for that contingency). Conditions: authored last; strict full-schema comparison; regeneration policy recorded. Uses pandas.testing only — no new dependencies.

## Numerical verification

Golden rows derived from the accepted formula text (SI = 0.4375·ccs + 0.3125·eav_log + 0.25·cpr; eav_log = min(1, |ln r|/ln 2); ln 2 = 0.6931472):

| Inputs | Old output | New output | Derivation |
|---|---|---|---|
| COL (0.95, 0.93, 1.03, 0.02, w=1) | SI 0.13250 'low' | ccs 0.060, eav 0.042644, cpr 0.320, wm 0.2, SI 0.119576 'low' | ccs = 1−(0.95+0.93)/2; eav = ln 1.03/ln 2 = 0.0295588/0.6931472; cpr = 0.8·(0.02/0.05); SI = 0.026250+0.013326+0.080000 |
| BCS (0.72, 0.68, 1.45, 0.09, w=1) | SI 0.42070 'moderate' | ccs 0.300, eav 0.536053, cpr 0.816, wm 0.2, SI 0.502767 'high' | eav = ln 1.45/ln 2 = 0.3715636/0.6931472; cpr = 0.8+0.2·(0.04/0.5); SI = 0.131250+0.167517+0.204000 |
| A1C (0.85, 0.88, 1.10, 0.05, w=3) | SI 0.35225 'moderate' | ccs 0.135, eav 0.137504, cpr 0.800, wm 0.6, SI 0.302032 'moderate' | eav = ln 1.10/ln 2 = 0.0953102/0.6931472; SI = 0.059063+0.042970+0.200000 |
| aggregate_contract | {0.322, 0.3018, 0.4207, 3, 'moderate'} | {'weighted_shock_index': 0.3057, 'mean_shock_index': 0.3081, 'max_shock_index': 0.5028, 'measure_count': 3, 'risk_tier': 'moderate'} | weighted = (0.119576+0.502767+3·0.302032)/5 = 1.528440/5 = 0.305688; mean = 0.924375/3 = 0.308125; classify_risk(0.305688) = 'moderate' |

Detection property: the previously invisible ×0.9 mutation now fails with a per-cell diff (COL 0.107618 ≠ 0.119576).

## Implementation

Files: tests/golden/example_scored_golden.csv (new), tests/test_golden.py (new, two tests). Sequenced last (step 4).

## QA result

**Pass** (gate 2026-07-12, zero blocking findings). Skeptic re-derived every golden cell to
10 dp from this ADR's formula text (hand-rounded values sit ~4e-11 from execution, inside
atol 1e-9, rtol 0) and the aggregate dict (weighted 0.3056879881 → 0.3057, mean
0.3081250793 → 0.3081). Programmer-verifier confirmed the detection property live: under an
injected ×0.9 mutation both golden tests fail (COL 0.1076187 ≠ 0.1195764) while the
pre-batch suite was blind; suite restored bit-exact to 85 passed. Baseline oracle-absence
claim corroborated by exhaustive assertion inspection of git show HEAD:tests/.

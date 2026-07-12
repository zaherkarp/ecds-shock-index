# 0002 — Remove WM (exposure) from the measure-level composite; apply Stars weight once, at contract aggregation

- **Status**: accepted
- **Cycle**: 1
- **Proposer**: stat-methodologist
- **Component**: composite

## Context

`WM = measure_weight / max_weight` is an exposure/consequence indicator (how much a measure counts in Stars), not a hazard indicator, yet it enters the linear composite in `ShockIndexCalculator.calculate` (src/ecds_shock_index/__init__.py) with `delta_wm = 0.20` alongside three hazard components, while `aggregate_contract` already weights each `shock_index` by `measure_weight`. Weight therefore enters the contract index twice — additively inside each SI and multiplicatively at aggregation. Verified consequences: (1) a pure-exposure risk floor — a perfectly healthy weight-5 measure (ccs=eav=cpr=0) scores 0.2000; (2) rank inversions — that healthy measure outranks a weight-1 measure with genuine data-quality risk (0.2000 vs 0.1550); (3) double counting — two measures with identical hazards (0.3, 0.3, 0.3) and weights {1, 5} yield a contract weighted index of 0.4133 instead of the hazard-faithful 0.3000. Additive mixing also makes regulatory weight 'tradeable' against data quality, which is meaningless. All numbers independently re-derived from formula text by all four critics.

## Proposal

In `src/ecds_shock_index/__init__.py`, change `ShockIndexCalculator` defaults from (alpha_ccs=0.35, beta_eav=0.25, gamma_cpr=0.20, delta_wm=0.20) to **(alpha_ccs=0.4375, beta_eav=0.3125, gamma_cpr=0.25, delta_wm=0.0)** — the neutral proportional renormalization alpha/(1−0.20), preserving hazard ratios (0.4375/0.3125 = 0.35/0.25). Measure-level SI = 0.4375·ccs + 0.3125·eav + 0.25·cpr. `wm_score`, the `wm` column, and `__all__` unchanged (wm remains reported); exposure enters exactly once via the existing `weighted_shock_index = Σ SI_i·w_i / Σ w_i` — the standard hazard × exposure form. Rebuttal-revised atomic batch: class docstring (lines 150–152, 'favors completeness and measure weight' — becomes false and is rewritten); new default-sensitive test oracles (the originally named tests are vacuous: `test_calculate_weighted_index` uses explicit weights; sum-to-one passes at 0.4375+0.3125+0.25+0.0=1.0); README Quick Start/summary/CLI examples and weights table; blog `blog/ecds-shock-index.md` lines 35 and 42–50; docs/literature-evaluation.md weights description; notebook re-execution; CLI `--wm` becomes optional and ignored (deprecated) in single/legacy modes.

## Evidence

| Claim | Grade | Source | URL | Accessed | Supporting quote |
|---|---|---|---|---|---|
| Double counting inflates effective weight when one dimension enters twice | E1 (a-fortiori application: quote concerns two collinear indicators; here the identical variable enters twice) | OECD/JRC, Handbook on Constructing Composite Indicators (2008), p. 31 | https://www.oecd.org/content/dam/oecd/en/publications/reports/2008/08/handbook-on-constructing-composite-indicators-methodology-and-user-guide_g1gh9301/9789264043466-en.pdf | 2026-07-11 | "an element of double counting may be introduced into the index: if two collinear indicators are included in the composite index with a weight of w1 and w2, the unique dimension that the two indicators measure would have weight (w1 + w2) in the composite." |
| Linear-aggregation weights act as trade-offs; WM is not substitutable against data quality | E1 | OECD/JRC Handbook (2008), p. 33 | (same) | 2026-07-11 | "In both linear and geometric aggregations, weights express trade-offs between indicators. A deficit in one dimension can thus be offset (compensated) by a surplus in another." |
| Contract double-count and rank-inversion demonstrations | E3 | Hand arithmetic + repo runs, this cycle (proposer + 4 independent reproductions) | — | 2026-07-11 | "SI_w1=0.2800 SI_w5=0.4400 contract_weighted=0.4133 | proposed: SI_both=0.3000 contract_weighted=0.3000" |
| Weight-vector sensitivity (E4 value floor companion) | E3 | Referee-derived analytic bound + cycle sensitivity record (CAL-1 debate) | — | 2026-07-11 | See Numerical verification: at L1≤0.10 COL/A1C/contract labels provably stable; BCS margin 0.002767. |
| Renormalized vector (0.4375, 0.3125, 0.25) as the starting value | E4 | Expert judgment: the unique reweighting changing no hazard-vs-hazard trade-off | — | 2026-07-11 | Admissible only with the E3 sensitivity analysis above; CAL-1 re-run on the 3-weight simplex is next cycle's first agenda item. |

## Critiques

| Critic | Stance | Summary |
|---|---|---|
| stat-calibration | amend | Renormalized vector is still E4 and needs the sensitivity re-run; BCS margin to 'high' shrinks 0.0793→0.0241 (METH-1 alone); METH-1×METH-3 jointly flip BCS to 'high' (0.502767) — one combined oracle table required. |
| stat-domain-evidence | amend | Class docstring and lit-eval weights description become false and were missing from the batch; OECD p.31 is an a-fortiori application. All numbers reproduced. |
| stat-programmer | amend | Named test oracles are vacuous (patched-copy run: 60/60 pass under new defaults); post-change fixture oracles must be pinned; README/notebook target values must be stated. |
| stat-skeptic | amend | Blog is a breaking consumer omitted from the batch; CLI single example crosses a tier boundary (0.7220 'high' → 0.7525 'critical'); required `--wm` becomes a no-op and needs a migration decision. |

## Rebuttal

All amendments conceded and adopted: default-sensitive oracles replace the vacuous list; blog/docstring/README/lit-eval join the atomic batch; `--wm` optional + deprecated with migration note; OECD p.31 characterized a-fortiori with the E3 demonstration as the load-bearing evidence; single combined METH-1+METH-3 oracle table; renormalized vector defended only as the neutral starting value pending CAL-1 re-tuning.

## Verdict

**Accept.** Decisive evidence: the E3 contract double-count (0.4133 vs 0.3000) and rank-inversion demonstrations, re-derived from formula text by every critic. Conditions: co-land with ADR 0003 under one combined oracle table; this ADR embeds the 3-weight sensitivity disclosure below (E4 value admissible only alongside it), including the honest disclosure that BCS's post-batch 'high' label sits 0.002767 above the boundary and flips back at ||Δw||₁ ≥ ~0.011; CAL-1 tooling re-run on the 3-weight simplex is next cycle's first agenda item; `--wm` migration note covers README, notebook, and blog. No new dependencies.

## Numerical verification

| Inputs | Old output | New output | Derivation |
|---|---|---|---|
| Healthy wt-5 measure (0, 0, 0, wm=1.0) | 0.2000 ('low', pure-exposure floor) | 0.0000 | 0.20·1.0 = 0.2000 → 0.4375·0+0.3125·0+0.25·0 = 0 |
| Risky wt-1 (ccs 0.2, eav 0.1, cpr 0.1, wm 0.2) | 0.1550 (ranked below healthy wt-5) | 0.14375 (inversion removed) | 0.4375·0.2+0.3125·0.1+0.25·0.1 = 0.0875+0.03125+0.025 |
| Identical-hazard pair (0.3,0.3,0.3) × weights {1,5} | SIs {0.2800, 0.4400}; contract 0.41333 | SIs {0.3000, 0.3000}; contract 0.3000 | (0.4375+0.3125+0.25)·0.3 = 0.3000; (0.28·1+0.44·5)/6 = 0.41333 |
| Boundaries all-zero / all-one | 0.0 / 1.0 | 0.0 / 1.0 | weights sum to 1.0 |
| CLI single (0.86, 0.74, 0.58) | 0.7220 'high' | 0.7525 'critical' | 0.376250+0.231250+0.145000 |
| Fixture (combined with ADR 0003) | COL 0.13250 low, BCS 0.42070 mod, A1C 0.35225 mod; contract 0.322 | COL 0.119576 low, BCS 0.502767 high, A1C 0.302032 mod; contract 0.3057 | See ADR 0003 combined table |
| Sensitivity (E3, analytic) | — | COL/A1C/contract stable at L1≤0.10; BCS fragile | \|ΔSI\| ≤ (\|\|Δw\|\|₁/2)·range: bounds 0.013868/0.025800/0.033250 vs margins 0.130424/**0.002767**/0.052032; contract bound (0.013868+0.025800+3·0.033250)/5 = 0.027884 < 0.055688 |

## Implementation

Files: src/ecds_shock_index/__init__.py (defaults, class docstring), src/cli.py (--wm optional/deprecated in single/legacy), tests/test_core.py (NEW test_default_weights_exact: 0.4375/0.3125/0.25/0.0), README.md, blog/ecds-shock-index.md, docs/literature-evaluation.md (weights description + summary-table row), notebooks/00-overview.ipynb (re-executed). Fixture value oracles carried by ADR 0005's golden file.

## QA result

**Pass** (gate 2026-07-12, zero blocking findings). Skeptic re-derived all five verification
rows independently (exposure floor removed, rank inversion removed, contract double-count
0.4133→0.3000, CLI 0.7525 'critical' verified live, L1≤0.10 sensitivity bounds with BCS
margin 0.002767 confirmed fragile-as-disclosed). Both OECD/JRC quotes re-fetched verbatim
2026-07-12; a-fortiori labeling confirmed appropriate. `--wm` verified accepted-and-ignored
(0.7525 unchanged with --wm 1.0/0.9). Execution environment: Python 3.11.15, pandas 3.0.3
(pinning deferred to 0013).

# 0003 — Make EAV symmetric on the log scale: |ln(ratio/baseline)| / (sensitivity · ln 2)

- **Status**: accepted
- **Cycle**: 1
- **Proposer**: stat-methodologist
- **Component**: eav

## Context

`eav_score` (src/ecds_shock_index/__init__.py) uses the arithmetic deviation |ratio/baseline − 1| on a ratio-scale quantity. The code's docstring and the test name `test_below_baseline_is_symmetric` claim two-sided symmetric risk, but the form delivers it only additively: a halving (0.5) scores 0.5 while a doubling (2.0) scores 1.0, and the reciprocal pair 0.8/1.25 scores 0.20/0.25. Deflation risk is structurally understated (EAV cannot reach 1.0 downside until ratio = 0), an asymmetric effective scale feeding the weighted composite.

## Proposal

Replace with: `if variance_ratio <= 0: return 1.0` then `_clip_01(abs(math.log(variance_ratio / baseline)) / (sensitivity * math.log(2.0)))`. The ln 2 denominator preserves the saturation anchor (doubling → exactly 1.0 at default sensitivity) — a functional-form change, not a recalibration; saturation at ratio 2**sensitivity AND its reciprocal. Properties preserved: eav(baseline)=0, monotone in deviation each side, range [0,1]. Property gained: eav(r) = eav(1/r) exactly. Rebuttal-completed atomic batch: `test_above_baseline` (0.5 → 0.584963) and `test_sensitivity_scales_deviation` (0.25 → 0.292481) — both omitted from the original list and caught by two critics; the 0.5/2.0 oracle relabeled as a saturation check with the interior reciprocal pair eav(0.8)==eav(1.25)==0.321928 as the load-bearing symmetry oracle plus a reciprocal sweep; README lines 60/67; docs/literature-evaluation.md line 52's additive pair (1.45, 0.55) replaced entirely by the reciprocal pair (1.45, 0.6897) — a value-swap alone would have shipped a false symmetry claim; docstring rewrite; notebook re-execution.

## Evidence

| Claim | Grade | Source | URL | Accessed | Supporting quote |
|---|---|---|---|---|---|
| Log-change is the only symmetric, additive, normed indicator of relative change | E1 | Törnqvist, Vartia & Vartia, 'How Should Relative Changes Be Measured?', ETLA DP No. 68 (author version of Am. Stat. 39(1), 1985) — fetched, verbatim; skeptic confirmed dp681.pdf is DP 68 | https://www.etla.fi/wp-content/uploads/dp681.pdf | 2026-07-11 | "It is shown that the log-change ... is the only symmetric, additive and normed indicator of relative change." |
| Normalization must render indicators comparable; skewed inputs accounted for | E1 | OECD/JRC Handbook (2008), checklist p. 15 | https://www.oecd.org/content/dam/oecd/en/publications/reports/2008/08/handbook-on-constructing-composite-indicators-methodology-and-user-guide_g1gh9301/9789264043466-en.pdf | 2026-07-11 | "Normalisation. Indicators should be normalised to render them comparable. ... Skewed data should also be identified and accounted for." |
| 9-point before/after table incl. boundaries; reproduced exactly by 3 independent roles | E3 | Hand re-derivations from formula text, this cycle | — | 2026-07-11 | "ratio=2.0: 1.0000/1.0000 | ratio=0.5: 0.5000/1.0000 | ratio=1.45: 0.4500/0.5361 | ratio=0.8 vs 1.25: 0.20/0.25 → both 0.3219" |
| k-fold compression and inflation equally distort CMS cluster geometry | E4 | Labeled judgment (per skeptic amendment); primary support is the E1 measurement-theory citation plus the code's own declared symmetry intent | — | 2026-07-11 | — |

## Critiques

| Critic | Stance | Summary |
|---|---|---|
| stat-calibration | amend | Support; sensitivity semantics change (saturation at 2**s) must be documented; METH-1 interaction flips BCS to 'high' (0.502767) — combined table required; margins tighten. |
| stat-domain-evidence | amend | Support; lit-eval line 52's companion claim '0.55 → 0.45 (symmetric)' becomes false (0.55 → 0.8625) and was unlisted; docstring saturation sentence needs rewriting. |
| stat-programmer | amend | Two unlisted failing oracles (test_above_baseline, test_sensitivity_scales_deviation); the 0.5/2.0 oracle is nearly vacuous as a symmetry test; fixture/README/notebook drift unlisted. |
| stat-skeptic | amend | Same failing oracles plus README line 60/67; the reciprocal of 1.45 is 0.6897, not 0.55; cluster-geometry equivalence is asserted, not evidenced — label E4. |

## Rebuttal

All concessions made; completed inventory adopted wholesale; E4 label accepted with the note that the change rests on the E1 citation plus the code's declared symmetry intent, not the clustering claim; combined oracle table with METH-1 accepted.

## Verdict

**Accept.** Formula-change floor met: E1 methodology citation (quote-checked verbatim by two independent fetches) + E3 before/after table with 9 points including boundaries, reproduced exactly by three roles. Co-lands with ADR 0002 under the single combined oracle table below. Conditions: interior reciprocal pair is the load-bearing symmetry oracle; lit-eval pair replaced, not value-swapped; E4 label on the clustering-equivalence sentence; BCS boundary fragility (margin 0.002767) disclosed jointly with ADR 0002.

## Numerical verification

| Inputs | Old output | New output | Derivation |
|---|---|---|---|
| r = 1.0 | 0.0 | 0.0 | ln 1 = 0 |
| r = 2.0 / r = 0.5 | 1.0 / 0.5 | 1.0 / 1.0 | ln 2/ln 2 = 1; \|ln 0.5\|/ln 2 = 1 (saturation now reciprocal) |
| r = 0.8 vs 1.25 | 0.20 vs 0.25 | 0.321928 both | \|ln 0.8\| = ln 1.25 = 0.2231436; /0.6931472 |
| r = 1.5; (s = 2) | 0.5; 0.25 | 0.584963; 0.292481 | 0.4054651/0.6931472; halved |
| r = 1.45; r = 0.6897; r = 0.55 | 0.45; 0.3103; 0.45 | 0.536053; 0.536053; 0.862496 | ln 1.45 = 0.3715636; 1/1.45 = 0.689655; \|ln 0.55\| = 0.5978370 |
| r = 1.15 (README) | 0.15 | 0.201634 | 0.1397619/0.6931472 |
| r ≤ 0 | 1.0 (via clip) | 1.0 (explicit guard) | — |
| Combined fixture (with ADR 0002) | COL 0.13250/BCS 0.42070/A1C 0.35225; contract 0.322 | COL 0.119576 low / BCS 0.502767 high / A1C 0.302032 mod; contract 0.3057 mod, mean 0.3081, max 0.5028 | COL: 0.4375·0.060+0.3125·0.042644+0.25·0.320; BCS: 0.131250+0.167517+0.204000; A1C: 0.059063+0.042970+0.200000; weighted (0.119576+0.502767+3·0.302032)/5 = 1.528440/5 |

## Implementation

Files: src/ecds_shock_index/__init__.py (eav_score + docstring), tests/test_core.py (oracles above), README.md (lines 60, 67), docs/literature-evaluation.md (line 52 + summary-table row), notebooks/00-overview.ipynb. Fixture pinning via ADR 0005's golden.

## QA result

**Pass** (gate 2026-07-12, zero blocking findings). Skeptic re-derived eav(1.5)=0.5849625007,
the reciprocal pair 0.8/1.25 → 0.3219280949, reciprocal saturation at 2.0/0.5, the lit-eval
replacement values (1.45 and 0.6897 → 0.5360529; 0.55 → 0.8624965, confirming the old pair
was not reciprocal), and README eav(1.15)=0.2016339. ETLA dp681.pdf re-fetched 2026-07-12;
Törnqvist/Vartia/Vartia quote confirmed verbatim in the OCR text layer. All fixture eav
deltas attributed to this ADR by column-level behavior diff.

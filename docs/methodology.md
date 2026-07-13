# ECDS Shock Index Methodology

This document provides a complete technical description of the ECDS Shock Index
methodology as of cycle 2 (July 2026), including formulas, parameter choices, aggregation
design, and the evidence behind each decision. For the evolution history, see
[`literature-evaluation.md`](literature-evaluation.md); for the governance process, see
[`statistical-governance.md`](statistical-governance.md).

## Overview

The ECDS Shock Index quantifies the distribution-shift risk that Electronic Clinical Data
Systems (ECDS) adoption introduces into Medicare Advantage Star Ratings. It combines three
**hazard** components — data completeness gaps, adoption variability, and cutpoint
pressure — into a single [0, 1] score per measure, then aggregates to contract level
using CMS measure weights as the exposure dimension.

```
Measure-level:   SI = alpha * CCS + beta * EAV + gamma * CPR
Contract-level:  SI_contract = sum(SI_i * weight_i) / sum(weight_i)
```

## Component formulas

### CCS — Clinical Completeness Gap Score

**Purpose:** Captures how far a measure's electronic data capture falls short of
complete coverage. NCQA guidance identifies incomplete or poorly-mapped capture as the
dominant ECDS-transition risk.

**Formula:**

```
CCS = 1 - (completeness_rate + mapping_coverage) / 2
```

**Domain:** CCS in [0, 1]. Perfect capture (1.0, 1.0) scores 0.0 (no risk). Fully
missing (0.0, 0.0) scores 1.0 (maximum risk).

**Example:** completeness = 0.95, mapping = 0.93 -> CCS = 1 - (0.95 + 0.93)/2 = 0.06.

**Evidence:** NCQA ECDS reporting guidance; direction corrected from raw average to gap
in the initial literature evaluation.

---

### EAV — ECDS Adoption Variability

**Purpose:** Measures how much a measure's distribution has shifted from its stable
baseline — in either direction. CMS clustering depends on reasonably stable
distributions, so both inflation and deflation of variance are risk signals.

**Formula:**

```
EAV = |ln(variance_ratio / baseline)| / (sensitivity * ln 2)
```

Clipped to [0, 1]. A non-positive `variance_ratio` is degenerate and scores 1.0.

**Key property:** Reciprocal symmetry — `eav(r) = eav(1/r)`. A k-fold inflation and
k-fold compression carry identical risk. This follows from the log-change being the only
symmetric, additive, normed indicator of relative change (Tornqvist, Vartia & Vartia,
1985).

**Parameters:**
- `baseline` (default 1.0): reference variance ratio representing stability.
- `sensitivity` (default 1.0): controls the saturation point. With sensitivity = 1.0,
  the score saturates at a doubling or halving (`2^sensitivity` and its reciprocal).

**Example:** variance_ratio = 1.45 -> EAV = |ln(1.45)| / ln(2) = 0.5361.
Reciprocal check: 1/1.45 = 0.6897 -> EAV = |ln(0.6897)| / ln(2) = 0.5361.

**Evidence:** Tornqvist et al. 1985; adopted via [ADR-0003](decisions/0003-log-symmetric-eav.md).

---

### CPR — Cutpoint Pressure Risk (guardrail-aware)

**Purpose:** Quantifies the risk from cutpoint movement, structured around the CMS
guardrail that caps realized year-over-year movement.

**CMS guardrail rule:** Cut-point changes are capped at 5 percentage points for measures
on a 0-100 scale, or 5% of the prior year's restricted score range otherwise. Guardrails
are NOT applied to improvement measures or to measures in the program 3 years or less.

**Formula:**

```
realized = min(|shift|, guardrail) / guardrail
latent   = max(|shift| - guardrail, 0) / max_shift
CPR      = (1 - L) * realized + L * latent
```

where `L = latent_share` (default `CPR_LATENT_SHARE_DEFAULT = 0.20`).

**Design rationale:** The realized term saturates at the guardrail — a shift at or beyond
the cap consumes the full realized share. The latent term captures deferred pressure from
movement beyond the guardrail, which re-surfaces in later Star years when the guardrail
relaxes. The 80/20 split (L = 0.20) is an E4 expert judgment; `latent_share` is exposed
as a public parameter for sensitivity analysis.

**Degenerate boundary:** At L = 1.0, the realized term vanishes. A shift exactly at the
guardrail scores 0.0 because the entire component is assigned to latent pressure, which
is zero when no excess exists.

**Parameters:**
- `guardrail` (default 0.05): the CMS cap in fraction units.
- `max_shift` (default 0.5): normalizer for the latent term.
- `latent_share` (default 0.20): realized/latent split in [0, 1].

**Examples:**
| Shift | Realized | Latent | CPR (L=0.20) |
|-------|----------|--------|--------------|
| 0.00  | 0.00     | 0.00   | 0.00         |
| 0.02  | 0.40     | 0.00   | 0.32         |
| 0.05  | 1.00     | 0.00   | 0.80         |
| 0.09  | 1.00     | 0.08   | 0.82         |
| 0.55  | 1.00     | 1.00   | 1.00         |

**Evidence:** CMS 2026 Technical Notes; guardrail-aware design via initial literature
evaluation; parameter exposure via [ADR-0008](decisions/0008-expose-cpr-latent-share.md);
wording corrections via [ADR-0011](decisions/0011-guardrail-eligibility-and-cap-wording.md).

---

### WM — Weight Multiplier (exposure indicator)

**Purpose:** Normalizes the CMS Stars measure weight to [0, 1] as an exposure indicator.

**Formula:**

```
WM = measure_weight / max_weight
```

**CMS weight categories (2026):** process = 1, intermediate/outcome = 3,
patient-experience/access = 2 (reduced from 4), improvement = 5.

**Role in the index:** WM does NOT enter the measure-level composite. It is reported per
measure and applied exactly once — as the aggregation weight in the contract-level rollup
(hazard x exposure). This avoids double-counting weight, which the OECD/JRC Handbook on
Constructing Composite Indicators warns against. See
[ADR-0002](decisions/0002-remove-wm-from-measure-composite.md).

---

## Composite aggregation

### Measure level

The measure-level shock index is a linear-additive weighted average of the three hazard
components:

```
SI = alpha * CCS + beta * EAV + gamma * CPR
```

**Default weights:**

| Weight    | Value  | Component |
|-----------|--------|-----------|
| alpha     | 0.4375 | CCS       |
| beta      | 0.3125 | EAV       |
| gamma     | 0.25   | CPR       |

These are the neutral renormalization of the original hazard weights (0.35, 0.25, 0.20)
after removing WM from the composite (dividing by 1 - 0.20 = 0.80), preserving relative
importance. They are E4 judgments — no empirical calibration yet — but
[weight sensitivity analysis](#weight-sensitivity-analysis) confirms local robustness.

**Compensability assumption:** Linear aggregation is fully compensatory — a low score on
one component offsets a high score on another. This is appropriate for an early-warning
index where the overall risk posture matters more than any single dimension.

### Contract level

```
SI_contract = sum(SI_i * measure_weight_i) / sum(measure_weight_i)
```

This is a weighted average across all scored measures, using CMS Stars measure weights as
the aggregation weights. Higher-weight measures (improvement = 5, outcome = 3) contribute
proportionally more to the contract-level risk.

The contract-level summary also reports `mean_shock_index` (unweighted), `max_shock_index`
(worst-case measure), and `measure_count`.

---

## Risk tiers

| Tier     | Score range    | Interpretation                                     |
|----------|----------------|----------------------------------------------------|
| Low      | [0.00, 0.25)   | Minimal distribution risk; ECDS transition on track |
| Moderate | [0.25, 0.50)   | Some volatility; monitor cutpoint movement          |
| High     | [0.50, 0.75)   | Significant risk; prioritize remediation            |
| Critical | [0.75, 1.00]   | Severe exposure; immediate action recommended       |

Cutpoints are equal-width (0.25 increments). These are operational defaults; the decision
log includes a deferred proposal ([ADR-0009](decisions/0009-tier-margin-reporting.md)) for
reporting tier margins to quantify how close a measure is to a boundary.

---

## Weight sensitivity analysis

The `weight_sensitivity()` function ([ADR-0007](decisions/0007-weight-sensitivity-tooling.md))
addresses the OECD/JRC Handbook step-7 requirement for robustness assessment.

**One-at-a-time (OAT) perturbation:** For each weight, perturb by +/- delta while
renormalizing the remaining weights proportionally on the simplex. Default deltas:
0.05, 0.10, 0.20.

**Key findings (on the 3-measure example fixture):**
- BCS (Breast Cancer Screening) straddles the high/moderate boundary at SI = 0.5028 with
  a margin of only 0.0028.
- BCS flips from high to moderate at an L1 radius of ~0.01535 on the weight simplex —
  a ~3% relative change in alpha_ccs.
- At L1 <= 0.10, zero tier flips occur — the defaults are locally robust.
- Validity domain radius for the default weights: 0.50 (= 2 * min(alpha, gamma)).

**Dirichlet(1,1,1) Monte Carlo:** The analysis script (`scripts/weight_sensitivity_analysis.py`)
also samples 200,000 weight vectors uniformly from the 3-simplex (stdlib `random`,
seed 7) to characterize global tier-flip frequency.

**Usage:**

```python
from ecds_shock_index.sensitivity import weight_sensitivity

oat_results = weight_sensitivity(scored_df, deltas=(0.05, 0.10, 0.20))
flips = oat_results[oat_results["tier_flip"]]
```

---

## Input validation

All scoring functions reject non-finite inputs (NaN, +/-inf) with `ValueError`
([ADR-0004](decisions/0004-reject-nonfinite-inputs.md)). The batch pipeline
(`score_dataframe`) additionally rejects NaN in any required column — e.g., a
`measure_weight` that is NaN after merging an ECDS measure_id with no row in the
weights file. This prevents silently laundering missing data into a [0, 1] risk score.

---

## Test oracles

Every test expectation is derived from the ADR formula text by hand arithmetic, never
from running the implementation ([ADR-0005](decisions/0005-golden-file-batch-oracles.md)).
The golden file (`tests/golden/example_scored_golden.csv`) is compared with
`assert_frame_equal(atol=1e-9, rtol=0)` and full column-order schema enforcement.

Current test count: 95 (as of cycle 2).

---

## Decision log

All methodology changes are recorded in [`docs/decisions/`](decisions/) with full evidence
trails. See the [index](decisions/README.md) for the complete list.

| Cycle | ADRs accepted | Summary |
|-------|---------------|---------|
| 0     | 0001          | Adopt statistical governance framework |
| 1     | 0002-0005     | Hazard-only composite, log-symmetric EAV, non-finite rejection, golden-file oracles |
| 2     | 0007-0008, 0010-0011 | Weight sensitivity tooling, CPR latent share parameter, health-equity closure, guardrail wording |

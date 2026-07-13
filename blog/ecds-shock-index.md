---
title: "The ECDS Shock Index: Modeling Distribution Risk in Medicare Advantage Stars"
date: "2026-02-14"
updated: "2026-07-13"
author: "ECDS Shock Index Team"
tags: ["medicare-advantage", "stars", "ecds", "quality-measurement", "analytics"]
summary: "A practical framework for quantifying risk when ECDS data shifts Stars measure distributions and cutpoints."
---

# The ECDS Shock Index: Modeling Distribution Risk in Medicare Advantage Stars

As Medicare Advantage quality programs evolve, plans are being pushed to operationalize Electronic Clinical Data Systems (ECDS) and digital quality methods at scale. That transition promises richer, more complete measure capture--but it also introduces volatility in measure distributions, benchmarking behavior, and cutpoint movement.

Most teams are prepared to improve raw measure rates. Fewer are prepared to quantify *distribution risk*.

That is the purpose of the **ECDS Shock Index**.

## Why a Shock Index?

Stars outcomes are relative and threshold-based. This means an organization can improve absolute performance while still losing competitive position when:

1. peer distributions shift faster,
2. coding and data completeness effects are uneven,
3. high-weight measures amplify small changes,
4. cutpoints move due to changes in numerator/denominator behavior across the market.

The ECDS Shock Index is a compact way to represent these dynamics as one interpretable risk score.

## Conceptual Components

We define four components, each normalized to a 0--1 **risk** scale (higher = more risk):

- **CCS (Clinical Completeness Gap):** The gap between perfect and actual data completeness/mapping. Incomplete capture is the dominant ECDS-transition risk, so *less* complete data scores higher.
- **EAV (ECDS Adoption Variability):** How far the distribution deviates from its stable baseline in either direction, measured on the log scale so a k-fold compression and a k-fold inflation carry identical risk; a stable distribution carries no adoption-variability risk.
- **CPR (Cutpoint Pressure Risk):** Expected cutpoint movement, anchored to the CMS guardrail that caps realized year-over-year movement at 5 percentage points (0--100 scale) or 5% of the prior year's restricted score range; guardrails do not apply to improvement measures or measures in the program 3 years or less. Movement beyond the guardrail represents latent pressure deferred to later Star years. The realized/latent split is controlled by the `latent_share` parameter (default 0.20), now publicly tunable for sensitivity analysis.
- **WM (Weight Multiplier):** How strongly Stars weighting amplifies the impact of that measure (process = 1, outcome = 3, improvement = 5; patient experience = 2 as of 2026). WM is an *exposure* indicator, reported alongside the hazard components; it enters the contract-level rollup as the aggregation weight rather than the measure-level composite.

> The clinical shock index (Allgower & Buri, 1967) is a *ratio* of heart rate to systolic blood pressure. This index borrows the "compact early-warning signal" idea but is a weighted *composite*, not a ratio.

The measure-level composite is hazard-only:

\[
\text{ShockIndex} = \alpha \cdot CCS + \beta \cdot EAV + \gamma \cdot CPR
\]

In the current implementation:

- \(\alpha = 0.4375\)
- \(\beta = 0.3125\)
- \(\gamma = 0.25\)

Stars measure weight (WM's underlying quantity) then enters exactly once, at
contract-level aggregation, as the weight in the hazard x exposure rollup --
an earlier version also included WM additively in the measure composite,
which double-counted weight and let a measure's regulatory importance masquerade
as data risk (see `docs/decisions/0002-remove-wm-from-measure-composite.md`).
The weights can be tuned based on governance preferences and empirical
back-testing; every change is debated and logged under `docs/decisions/`.

## Weight Sensitivity Analysis

How robust are the default weights? The `weight_sensitivity` module answers this with
two complementary methods:

- **One-at-a-time (OAT) perturbation:** Perturb each weight by +/- delta while
  renormalizing the others on the simplex. At delta = 0.05 (a ~10% relative change),
  BCS flips from "high" to "moderate" -- the only tier flip in the example fixture.
  The critical L1 radius for this flip is ~0.01535, confirming BCS is the most
  fragile measure under weight perturbation.

- **Dirichlet(1,1,1) Monte Carlo:** 200,000 weight vectors sampled uniformly from the
  3-simplex characterize global tier-flip frequency. Within an L1 ball of radius 0.10
  around the defaults, zero tier flips occur -- the weights are locally robust.

This tooling fulfills the OECD/JRC Handbook step-7 requirement for sensitivity analysis
of composite weights.

## Practical Uses

Plans can use the ECDS Shock Index to:

- prioritize measure-level remediation where volatility risk is highest,
- test star-level sensitivity under cutpoint simulation,
- quantify weight sensitivity to understand how fragile risk classifications are,
- communicate technical risk to quality and finance leadership,
- track readiness as ECDS pipeline maturity improves.

## What This Repository Includes

This repository provides a complete implementation with:

- a Python package for core component calculations (`src/ecds_shock_index/`),
- weight-sensitivity analysis module and analysis script (`sensitivity.py`, `scripts/`),
- data loading utilities for NCQA ECDS and CMS weight data,
- a CLI for single-measure and batch scoring with JSON output,
- notebook scaffolding for exploratory analysis,
- 95 unit tests with hand-derived, oracle-pinned expectations,
- full methodology documentation and an evidence-graded decision log (13 ADRs across 3 review cycles).

## Next Steps

The framework continues to evolve through evidence-gated review cycles. Key areas:

- **Compensation alerts** -- a non-compensatory companion signal that flags when a low
  score on one component masks a high score on another (ADR-0006, deferred).
- **Tier margin reporting** -- quantifying how close each measure is to a tier boundary,
  so users can distinguish a solid "high" from a knife-edge classification (ADR-0009).
- **Guardrail-exempt CPR mode** -- a two-regime form that correctly prices measures
  exempt from CMS guardrails (improvement measures, measures in program <= 3 years).
- **Historical back-testing** -- calibrating weights against 3--5 historical Stars years.
- **Visualization templates** -- executive dashboards and operational drill-downs.

If your team is preparing for the next phase of quality measurement modernization, we hope this framework helps you move from intuition to quantified risk.

## Evidence Base

Each component direction and parameter is grounded in the published CMS Star Ratings and NCQA HEDIS ECDS literature -- cut-point guardrails and Tukey outlier deletion, the 2026 measure-weight changes, and the NCQA hybrid-to-digital transition timeline. See [`docs/literature-evaluation.md`](../docs/literature-evaluation.md) for the full review and references, and [`docs/methodology.md`](../docs/methodology.md) for the complete technical specification.

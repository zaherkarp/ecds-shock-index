# Next Steps for Improvement

This document tracks the roadmap for the ECDS Shock Index beyond cycle 2 (July 2026).
Items are organized by priority tier. Each deferred item has an ADR on file in
[`docs/decisions/`](decisions/) with its evidence state and the reason for deferral.

## Priority 1 — Deferred ADRs (cycle 3 agenda)

These items were considered in cycles 1-2 and deferred on cap or sequencing grounds, not
on merit. They form the opening agenda for the next review cycle.

### ADR-0006: Non-compensatory compensation alert

**Status:** Deferred (cycles 1, 2).

**What:** Append a boolean `compensation_alert` flag to each scored measure indicating
whether a low score on one hazard component is masking a high score on another. Report
`n_compensation_alerts` in the contract-level summary.

**Why it matters:** The linear-additive composite is fully compensatory — a measure can
score "moderate" overall while having a critical-level CPR offset by a low CCS. A
non-compensatory companion signal surfaces these hidden concentrations without changing
the composite formula.

**Blocked by:** Was originally designed against the 4-weight composite; needs re-derivation
against the 3-hazard-weight simplex and new fixture truth table.

### ADR-0009: Tier margin reporting

**Status:** Deferred (cycles 1, 2).

**What:** Add a `tier_margin` column to scored DataFrames and a `tier_margin` key to
contract-level JSON output, reporting the distance from the nearest tier boundary.

**Why it matters:** BCS scores 0.5028 ("high") with a margin of only 0.0028 above the
high/moderate boundary. Without the margin, users cannot distinguish a solid "high" from
a knife-edge classification. Weight sensitivity analysis (ADR-0007) confirmed this
fragility — BCS flips tier at an L1 radius of ~0.01535.

**Depends on:** ADR-0007 (landed); ready to implement.

### ADR-0012: First-year weight-1 rule documentation

**Status:** Deferred (cycles 1, 2).

**What:** Document that CMS assigns weight 1 to measures in their first year in the Star
Ratings program, regardless of their eventual category. Reframe the impact as a
contract-level aggregation-share distortion rather than a measure-level scoring issue.

**Why it matters:** A measure scored at weight 3 (outcome) that is actually in its first
year (weight 1) will be over-weighted in `aggregate_contract`, distorting the
contract-level index.

### ADR-0013: Pin reference environment and CI version matrix

**Status:** Deferred (cycles 1, 2).

**What:** Add `requires-python >= 3.11` to `pyproject.toml`, a CI matrix testing
3.11-3.13, and a `constraints.txt` pinning pandas/numpy/pytest versions.

**Why it matters:** Reproducibility across environments. Currently no version floor or
CI matrix.

**Note:** This is a breaking change (requires migration note).

---

## Priority 2 — Near-term enhancements

### Guardrail-exempt CPR mode

**What:** A two-regime CPR form that applies the guardrail to eligible measures and uses
unguardrailed linear scoring for exempt measures (improvement measures and measures in the
program 3 years or less).

**Why it matters:** The current single-regime form misprices exempt measures. A shift of
0.15 for an improvement measure scores 0.84 under the guardrail-aware formula, but the
CMS guardrail does not actually apply — the mechanism-consistent score would be ~0.30.

**Status:** Identified during cycle-2 review; handed to the methodologist for design.
Requires a `guardrail_exempt` boolean column in the ECDS input CSV.

### Probabilistic cutpoint scenarios

**What:** Monte Carlo simulation of cutpoint movement under different distribution-shift
assumptions, producing confidence intervals on the shock index rather than a point
estimate.

**Why it matters:** The current CPR uses a single observed or expected shift. In
practice, cutpoint movement is uncertain — plans need to understand the range of
plausible outcomes.

### Historical back-testing

**What:** Calibrate composite weights and sensitivity parameters against 3-5 historical
Star Ratings years by measuring how well the shock index would have predicted actual tier
movements.

**Why it matters:** The current weights are E4 expert judgments. Empirical calibration
would promote them to E3 (with E1 data sources) and provide a principled basis for
weight selection. Sensitivity tooling (ADR-0007) is the prerequisite — now landed.

---

## Priority 3 — Longer-term capabilities

### Visualization and reporting

- Executive dashboard template (contract-level heatmap, measure waterfall chart)
- Operational drill-down (component-level bar chart per measure, trend over time)
- Exportable PDF/HTML report with risk narrative

### Multi-contract portfolio view

- Score and compare multiple contracts side-by-side
- Identify portfolio-level concentration risk (e.g., all contracts exposed to the same
  high-CPR measures)

### Integration hooks

- API endpoint for real-time scoring against a live data pipeline
- Webhook/alert when a measure crosses a tier boundary or margin threshold
- Integration with existing Stars analytics platforms

### Health equity re-evaluation

- **Closed for 2027** ([ADR-0010](decisions/0010-close-health-equity-component.md)). CMS
  is not implementing the Excellent Health Outcomes for All (EHO4all) reward for the 2027
  Star Ratings and continues the historical reward factor.
- Re-evaluate only if CMS finalizes an implementation year for EHO4all or a successor
  mechanism. When/if re-opened, the component would model the risk that health equity
  adjustments introduce into measure-level or contract-level star calculations.

---

## Contributing

Methodology changes follow the governance process in
[`docs/statistical-governance.md`](statistical-governance.md). To propose a change:

1. File an issue or draft an ADR following [`docs/decisions/TEMPLATE.md`](decisions/TEMPLATE.md).
2. Include evidence at the appropriate grade (E1 for domain facts, E1/E2 + E3 for
   formulas, E3 + E4 for parameters).
3. The standing review team evaluates proposals in batch cycles.

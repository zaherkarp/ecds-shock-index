# Literature Evaluation of the ECDS Shock Index

This document reviews the published literature that the ECDS Shock Index models —
CMS Medicare Advantage Star Ratings methodology, NCQA HEDIS ECDS reporting, and the
clinical origin of the "shock index" metaphor — and evaluates each component of the
framework against it. Where the framework diverged from the evidence, the
corresponding change has been implemented in `src/ecds_shock_index/__init__.py`; the
rationale and before/after behavior are recorded here.

## Method

We reviewed: the CMS Part C & D Star Ratings Technical Notes and annual fact sheets
(cut-point methodology and measure weights), the CMS Star Ratings Measures & Weights
files, NCQA's HEDIS ECDS reporting resources and hybrid-retirement timeline, industry
analyses of cut-point dynamics, and the original clinical shock-index literature. Full
citations are in [References](#references).

## Program context

- **Cut-point mechanics.** For non-CAHPS measures, CMS sets star thresholds with a
  mean-resampling hierarchical clustering algorithm, applies **Tukey outer-fence
  outlier deletion** (outliers beyond 3.0 × IQR below Q1 / above Q3, effective with the
  2024 Star Ratings), and constrains year-over-year movement with **guardrails** that
  cap cut-point changes at **±5%** for measures with at least three years of data.
  These mechanics mean realized single-year cut-point movement is *bounded*, not free.
- **Measure weights.** CMS weights are categorical: process = 1, intermediate/outcome =
  3, the improvement measures = 5, and **patient-experience/access measures = 2 as of
  the 2026 Star Ratings** (reduced from 4×).
- **ECDS transition.** NCQA is retiring the hybrid method by **MY2029** and moving HEDIS
  fully digital by **MY2030**; ECDS-reportable measures rose from **19 (MY2025) to 25
  (MY2026)**. NCQA guidance identifies **incomplete or poorly-mapped electronic data
  capture** as the dominant risk when a measure transitions to ECDS.

## Component-by-component evaluation

### CCS — Clinical Completeness *Gap* Score
- **Finding.** Incomplete/poorly-mapped capture *raises* ECDS-transition risk.
- **Prior behavior.** CCS returned the *average* of completeness and mapping coverage
  and entered the composite with a positive weight (α = 0.35) — so **more complete data
  produced a higher risk score**, the opposite of the evidence.
- **Change.** CCS is now a completeness **gap**, `1 − mean(completeness, mapping)`.
  Perfect capture → 0.0 (no risk); fully missing → 1.0. Example: completeness 0.95,
  mapping 0.93 now scores **0.06** (was 0.94).

### EAV — ECDS Adoption Variability
- **Finding.** A stable distribution is low-risk; CMS clustering itself depends on
  reasonably stable distributions, so deviation in either direction is the risk signal.
- **Prior behavior.** A stable distribution (`variance_ratio = 1.0`) mapped to **0.5**,
  overstating baseline risk, and only upward variance increased risk.
- **Change.** EAV is the absolute deviation from baseline,
  `|variance_ratio/baseline − 1| / sensitivity` (default `sensitivity = 1.0`). Stable →
  0.0; a ratio of 1.45 → **0.45**; 0.55 → 0.45 (symmetric).

### CPR — Cutpoint Pressure Risk (guardrail-aware)
- **Finding.** CMS guardrails cap realized one-year cut-point movement (±5%), so risk
  should saturate near the guardrail rather than scale linearly to an arbitrary maximum.
- **Prior behavior.** Linear `|shift| / max_shift` with `max_shift = 0.5`, ignoring the
  guardrail entirely.
- **Change.** CPR splits into a guardrail-bounded *realized* term and a smaller *latent*
  term for movement beyond the cap (deferred to later Star years):
  `CPR = 0.8·min(|shift|, guardrail)/guardrail + 0.2·max(|shift| − guardrail, 0)/max_shift`
  with `guardrail = 0.05`. A shift of 0.02 → **0.32**; at the 0.05 guardrail → **0.80**;
  far beyond → up to 1.0. The 80/20 split is documented in code as `_CPR_LATENT_SHARE`.

### WM — Weight Multiplier
- **Finding.** CMS weights are categorical and the patient-experience weight dropped
  from 4 to 2 for 2026.
- **Evaluation.** The linear `weight / max_weight` normalization is sound; `max_weight =
  5.0` correctly corresponds to the improvement weight. No formula change — the
  docstring now records the current categorical schema, and the example weights use real
  CMS categories (process = 1, outcome = 3).

### Naming — "shock index"
- The clinical shock index (Allgöwer & Buri, 1967) is a **ratio** (heart rate ÷ systolic
  blood pressure). This framework is a **weighted composite**, not a ratio; the analogy
  conveys "a compact early-warning signal," and that distinction is now stated in the
  README and blog so the metaphor is not over-read.

## Summary of changes

| Component | Before | After | Evidence |
|-----------|--------|-------|----------|
| CCS | `mean(compl, map)` (complete = risky) | `1 − mean(compl, map)` (gap) | NCQA ECDS reporting guidance |
| EAV | stable → 0.5 | `\|ratio − 1\|/sensitivity`, stable → 0 | CMS clustering stability |
| CPR | linear `\|shift\|/0.5` | guardrail-bounded realized + latent | CMS guardrails (±5%) |
| WM | linear `weight/5` (docs only) | same math, schema documented | CMS 2026 weights |

## Future work (not implemented)
- A **health-equity risk** component reflecting the Health Equity Index that replaces the
  reward factor in upcoming Star years.
- **Empirical calibration** of the composite weights and `sensitivity`/`guardrail`
  parameters against historical Stars years (back-testing).

## References

1. CMS. *Medicare 2025 Part C & D Star Ratings Technical Notes* (updated 2024-10-03).
   https://www.cms.gov/files/document/2025-star-ratings-technical-notes.pdf
2. CMS. *2025 Medicare Advantage and Part D Star Ratings* (fact sheet).
   https://www.cms.gov/newsroom/fact-sheets/2025-medicare-advantage-part-d-star-ratings
3. CMS. *2026 Star Ratings Measures and Weights.*
   https://www.cms.gov/files/document/2026-star-ratings-measures.pdf
4. CMS. *2026 Star Ratings Fact Sheet.*
   https://www.cms.gov/files/document/2026-star-ratings-fact-sheet.pdf
5. RISE Health. *Star ratings and Tukey's disappearing act.*
   https://www.national.risehealth.org/insights-articles/star-ratings-and-tukey-s-disappearing-act/
6. NCQA. *HEDIS Electronic Clinical Data Systems (ECDS) Reporting.*
   https://www.ncqa.org/resources/hedis-electronic-clinical-data-systems-ecds-reporting/
7. NCQA. *Proposed Timeline for Retiring and Replacing HEDIS Hybrid Measures.*
   https://www.ncqa.org/blog/ncqas-proposed-timeline-for-retiring-and-replacing-hedis-hybrid-measures/
8. NCQA. *Understanding ECDS Reporting: Your Questions Answered.*
   https://www.ncqa.org/blog/understanding-ecds-reporting-your-questions-answered/
9. Allgöwer M, Buri C. "Schockindex." *Deutsche Medizinische Wochenschrift* 92 (1967):
   1947–1950. (Origin of the clinical heart-rate / systolic-pressure shock index.)
10. Tukey JW. *Exploratory Data Analysis.* Addison-Wesley, 1977. (Outer-fence outlier
    rule used in CMS cut-point clustering.)

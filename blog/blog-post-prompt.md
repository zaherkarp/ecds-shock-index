# Blog Post Prompt: ECDS Shock Index Cycle 2 Update

Use this prompt with an LLM or as a writing brief to generate a blog post about the
cycle 2 improvements to the ECDS Shock Index.

---

## Prompt

Write a blog post (1,200-1,800 words) for a Medicare Advantage quality analytics
audience -- Stars directors, quality VPs, analytics leads, and actuaries -- announcing
the cycle 2 update to the ECDS Shock Index framework. The tone should be technical but
accessible: assume the reader knows Stars basics (measures, weights, cutpoints, tiers)
but may not know composite-indicator methodology.

### Title suggestions (pick or adapt one)

- "Building a Defensible ECDS Risk Index: What We Changed and Why"
- "Weight Sensitivity, Guardrail Precision, and the Path to Calibrated ECDS Risk"
- "From Intuition to Evidence: How We Stress-Tested the ECDS Shock Index"

### Structure

**1. Opening (2-3 paragraphs)**
- Recap the problem: ECDS transition shifts measure distributions, cutpoints move, and
  plans need a quantitative early-warning signal.
- Introduce the ECDS Shock Index as a hazard-only composite of three components (CCS,
  EAV, CPR) with Stars weight entering once at contract aggregation.
- Set up the cycle 2 narrative: the framework now has evidence-gated governance, and
  this post covers the latest round of improvements.

**2. What changed in cycle 2 (the bulk of the post)**

Cover each of these four accepted ADRs. For each, explain (a) the problem it solved,
(b) the change, and (c) why it matters to a plan:

- **Weight sensitivity tooling (ADR-0007):** The composite weights (0.4375 / 0.3125 /
  0.25) were asserted without robustness analysis. New `weight_sensitivity()` module
  runs one-at-a-time perturbation on the 3-weight simplex and a 200,000-sample
  Dirichlet Monte Carlo. Key finding: BCS straddles the high/moderate boundary at
  SI = 0.5028 (margin 0.0028) and flips tier at an L1 radius of ~0.01535 -- but within
  a 10% L1 ball, zero flips occur. The weights are locally robust but the BCS fragility
  is real and disclosed. This fulfills OECD/JRC Handbook step 7.

- **CPR latent share parameter (ADR-0008):** The 80/20 realized/latent split in CPR was
  hardcoded as a private constant. Now it's a public `CPR_LATENT_SHARE_DEFAULT = 0.20`
  constant with a `latent_share` keyword on `cpr_score`, `score_dataframe`, and the CLI
  (`--latent-share`). This unblocks sensitivity analysis per OECD/JRC Handbook 1.7.
  At L = 1.0, the realized term vanishes -- a shift exactly at the guardrail scores 0.0,
  because the entire component is assigned to latent pressure. Include a small table
  showing CPR at L = 0.0, 0.20, 0.50, 1.0 for a shift of 0.05 (the guardrail).

- **Health equity component closure (ADR-0010):** CMS announced it is NOT implementing
  the Excellent Health Outcomes for All (EHO4all) reward for the 2027 Star Ratings
  (CMS-4208-F3/CMS-4212-F, April 2, 2026). The previously planned health-equity risk
  component was closed without build. Mention this as responsible governance: the team
  proposed it, tracked it, and closed it when the regulatory basis evaporated.

- **Guardrail wording corrections (ADR-0011):** The CMS guardrail rule -- 5 percentage
  points on a 0-100 scale, or 5% of the prior year's restricted score range; not applied
  to improvement measures or measures in the program 3 years or less -- was described
  inconsistently across 11 locations in code, docs, and blog. Three of those locations
  had the eligibility rule inverted ("applied to measures with >= 3 years" instead of
  "NOT applied to measures in the program 3 years or less"). All 11 locations now use
  the canonical long form from the CMS 2026 Technical Notes. No formula change, but
  docstring accuracy is part of defensibility.

**3. Governance in practice (1-2 paragraphs)**
- Briefly describe the process: 6-role statistician review team, evidence-graded debate,
  batch cap of 4 accepted per cycle, adversarial QA gate before commit.
- 13 ADRs on file across 3 cycles; 9 accepted, 4 deferred on sequencing (none rejected
  on merit). Every proposal leaves a paper trail.
- Link to `docs/statistical-governance.md` and `docs/decisions/`.

**4. What's next (2-3 bullet points)**
- Compensation alerts (ADR-0006): flagging when compensability hides concentrated risk.
- Tier margin reporting (ADR-0009): quantifying distance to the nearest tier boundary.
- Guardrail-exempt CPR mode: correctly pricing measures exempt from CMS guardrails.
- Historical back-testing: calibrating weights against past Stars years.

**5. Closing (1 paragraph)**
- The framework is open-source. Link to the repo. Invite teams preparing for MY2029/2030
  ECDS transition to try it and contribute.

### Key facts and numbers to include

| Fact | Value |
|------|-------|
| Composite weights | alpha=0.4375 (CCS), beta=0.3125 (EAV), gamma=0.25 (CPR) |
| WM default weight in composite | 0.0 (exposure enters at contract aggregation only) |
| CPR latent share default | 0.20 |
| CMS guardrail cap | 5 percentage points (0-100 scale) or 5% restricted range |
| Guardrail exemptions | Improvement measures; measures in program <= 3 years |
| BCS shock index (example) | 0.5028 ("high"), margin 0.0028 above moderate boundary |
| BCS tier-flip L1 radius | ~0.01535 |
| Dirichlet samples | 200,000 (seed 7, stdlib random) |
| Zero flips at L1 <= 0.10 | confirmed |
| Test count | 95 (hand-derived oracles, never fitted to implementation) |
| ADRs on file | 13 (9 accepted, 4 deferred) |
| Review cycles completed | 3 (cycle 0: governance; cycle 1: formulas; cycle 2: tooling + docs) |
| NCQA hybrid retirement | MY2029; fully digital by MY2030 |
| ECDS measures | 19 (MY2025) -> 25 (MY2026) |
| CMS patient-experience weight | 2 (reduced from 4 for 2026) |

### Source files to reference

- `docs/methodology.md` -- complete technical methodology
- `docs/literature-evaluation.md` -- literature review and evidence base
- `docs/statistical-governance.md` -- governance process
- `docs/decisions/README.md` -- decision log index
- `docs/next-steps.md` -- roadmap
- `src/ecds_shock_index/__init__.py` -- core scoring module
- `src/ecds_shock_index/sensitivity.py` -- weight sensitivity module
- `scripts/weight_sensitivity_analysis.py` -- analysis script

### Style notes

- No emojis.
- Use "Stars" (capitalized) for the CMS program; "star" (lowercase) for individual
  star ratings.
- Write "ECDS" not "eCDS".
- Prefer active voice and concrete numbers over vague claims.
- Include at least one worked numerical example (e.g., the BCS sensitivity story).
- End with a call to action, not a summary of what was covered.

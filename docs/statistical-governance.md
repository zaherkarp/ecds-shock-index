# Statistical Governance

This document governs how methodology changes are made to the ECDS Shock Index — its
formulas, parameters, risk tiers, and the tests that verify them. The goal is a
**statistically sound and defensible product**: every methodological choice either traces to
confirmed evidence or is explicitly labeled a judgment with its consequences quantified.

It is enforced by a standing team of statistician reviewer agents (below) whose review
cycles produce the decision log in [`docs/decisions/`](decisions/).

## The team

| Role | Definition | One-line charter |
|---|---|---|
| Methodologist | [`.claude/agents/stat-methodologist.md`](../.claude/agents/stat-methodologist.md) | Composite-indicator construction: normalization, aggregation/compensability, clipping, symmetry, tier design. |
| Calibration | [`.claude/agents/stat-calibration.md`](../.claude/agents/stat-calibration.md) | Free parameters, weights, sensitivity analysis, uncertainty. |
| Domain evidence | [`.claude/agents/stat-domain-evidence.md`](../.claude/agents/stat-domain-evidence.md) | CMS/NCQA regulatory facts embedded in code, docs, and data; re-fetches primary sources. |
| Programmer | [`.claude/agents/stat-programmer.md`](../.claude/agents/stat-programmer.md) | Test oracles, property-based invariants, golden files, reproducibility, numerical hygiene. |
| Skeptic | [`.claude/agents/stat-skeptic.md`](../.claude/agents/stat-skeptic.md) | Adversarial verification only: quote-checks citations, re-derives numbers, hunts breakage. No proposals, no verdicts. |
| Referee | [`.claude/agents/stat-referee.md`](../.claude/agents/stat-referee.md) | Debate chair; sole accept/reject/defer authority; enforces caps and the evidence floor. |

Orchestration lives in [`.claude/workflows/stat-team-cycle.js`](../.claude/workflows/stat-team-cycle.js)
(review → debate → rebuttal → verdict) and
[`.claude/workflows/stat-team-qa.js`](../.claude/workflows/stat-team-qa.js) (post-implementation gate).

## Evidence grades

| Grade | Meaning | Requirements |
|---|---|---|
| **E1** | Primary source, verified this cycle | CMS/NCQA publication, Federal Register, or peer-reviewed paper **fetched during the cycle**, with URL, access date, and a verbatim supporting quote. |
| **E2** | Secondary or cached source | Industry analysis, or a primary source cited in [`literature-evaluation.md`](literature-evaluation.md) that could not be re-fetched — marked "cached, not re-verified". |
| **E3** | In-repo numerical demonstration | A worked derivation, reproduction command, or sensitivity computation executed in this repository, with the arithmetic or command output shown. |
| **E4** | Labeled expert judgment | Admissible **only** for a parameter's chosen value, and only when accompanied by an E3 sensitivity analysis of that parameter. |

### Acceptance floor

- **Domain-factual change** (a regulatory fact in code/docs/data): requires **E1**. With
  only E2, the change may be accepted **provisional** and must be re-verified next cycle.
- **Formula change**: requires a methodology citation (E1 or E2) **and** E3 numerical
  verification — a before/after table with ≥3 input points including boundary cases.
- **Parameter change**: requires E3 sensitivity evidence (how outputs move with the
  parameter); E4 is allowed for the value itself alongside that analysis.
- A claim is **confirmed** when the skeptic independently reproduces the number from the
  formula text (not the implementation) **and** the citation quote-check passes.

## Debate protocol

One round each, no extensions:

1. **Proposal.** Each reviewer role independently submits ≤3 structured recommendations
   (schema in the role files), with evidence attached at submission time.
2. **Critique.** Every other reviewer role plus the skeptic files a written critique per
   recommendation: stance `support | oppose | amend`, argument, counter-evidence,
   verification attempted/result.
3. **Rebuttal.** The proposer answers opposing/amending critiques once — concessions and a
   revised proposal are allowed and encouraged.
4. **Verdict.** The referee issues `accept | reject | defer` per recommendation with written
   rationale naming the decisive evidence or critique, then sequences accepted items into a
   batch plan.

## Batch and QA loop

One **cycle** = review → debate → verdicts → batch implementation → QA gate → commit.

- **Caps**: ≤4 accepted recommendations per batch; one commit per batch; public API (names
  in `__all__`, CLI flags/defaults, CSV schemas) stable unless the ADR carries a migration
  note; oversized proposals are split or deferred.
- **QA gate** (must pass before the batch commit): full pytest suite green; CLI smoke
  (single, batch, legacy modes); notebook executes cleanly; skeptic re-derivations match;
  fixture behavior-diff fully attributed to ADRs; decision log complete. CI re-runs the
  suite on push.
- **Deferred items** automatically enter the next cycle's agenda. Cycles repeat until a
  review round yields no accepted material findings.

## Change rules

- A methodology change and its test-oracle update are **one atomic unit** — never committed
  separately. New oracle values are derived in the ADR from the accepted formula text, not
  from running the new code.
- Every changed formula or constant maps to **exactly one ADR** in `docs/decisions/`, and
  every accepted ADR appends a row to the summary table in
  [`literature-evaluation.md`](literature-evaluation.md).
- Rejected and deferred proposals get short-form ADRs too: the log shows what was
  considered, not just what won.

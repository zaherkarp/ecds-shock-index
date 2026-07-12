# 0001 — Adopt statistical governance framework

- **Status**: accepted
- **Cycle**: 0 (bootstrap)
- **Proposer**: repository owner
- **Component**: other

## Context

The ECDS Shock Index makes methodological claims — component formulas, composite weights
(0.35/0.25/0.20/0.20), a CPR latent share (0.20), risk-tier cutpoints (0.25/0.50/0.75) —
whose defensibility was previously maintained ad hoc through PR review.
[`../literature-evaluation.md`](../literature-evaluation.md) records one evidence-alignment
pass and itself flags empirical calibration and back-testing as unfinished. There was no
standing mechanism forcing new changes to meet an evidence bar, no adversarial verification
of numbers or citations, and no durable record of rejected alternatives.

## Proposal

Adopt the governance framework in [`../statistical-governance.md`](../statistical-governance.md):

- a six-role statistician team (methodologist, calibration, domain evidence, programmer,
  skeptic, referee) defined in `.claude/agents/`;
- an evidence-grading scheme (E1–E4) with an explicit acceptance floor per change type;
- a debate protocol (proposal → critique → rebuttal → referee verdict) run by
  `.claude/workflows/stat-team-cycle.js`;
- a batch/QA loop (≤4 accepted items per batch, atomic formula+oracle changes, QA gate via
  `.claude/workflows/stat-team-qa.js`) with this ADR log as the durable record.

## Verdict

Accepted (bootstrap decision by the repository owner; the framework governs all subsequent
methodology changes, including changes to itself).

## Implementation

`.claude/agents/*.md` (6 role files), `.claude/workflows/stat-team-cycle.js`,
`.claude/workflows/stat-team-qa.js`, `docs/statistical-governance.md`,
`docs/decisions/{README.md, TEMPLATE.md, 0001-adopt-statistical-governance.md}`, README
"Methodology governance" section.

## QA result

Framework commit is behavior-inert: full pytest suite green before and after; no `src/`
changes.

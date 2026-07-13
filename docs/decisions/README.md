# Decision Log

Architecture-decision-record (ADR) style log of every methodology proposal considered by the
statistician team — accepted, rejected, or deferred. Governed by
[`../statistical-governance.md`](../statistical-governance.md).

## Conventions

- **Numbering**: `NNNN-slug.md`, zero-padded, monotonically increasing, never reused.
- **Statuses**: `accepted` · `rejected` · `deferred` · `provisional` (accepted on E2
  "cached" evidence; must be re-verified next cycle) · `superseded (by NNNN)`.
- Accepted ADRs follow [`TEMPLATE.md`](TEMPLATE.md) in full; rejected/deferred ADRs may use
  the short form (Context, Proposal, decisive critique, Verdict).
- The index table below is updated every cycle and doubles as the cycle report.

## Index

| ADR | Title | Cycle | Verdict | Status |
|---|---|---|---|---|
| [0001](0001-adopt-statistical-governance.md) | Adopt statistical governance framework | 0 | accept | accepted |
| [0002](0002-remove-wm-from-measure-composite.md) | Remove WM (exposure) from the measure-level composite | 1 | accept | accepted |
| [0003](0003-log-symmetric-eav.md) | Make EAV symmetric on the log scale | 1 | accept | accepted |
| [0004](0004-reject-nonfinite-inputs.md) | Refuse non-finite inputs at the scoring boundary | 1 | accept | accepted |
| [0005](0005-golden-file-batch-oracles.md) | Freeze a formula-derived golden file for the batch pipeline | 1 | accept | accepted |
| [0006](0006-compensation-alert-companion-signal.md) | Non-compensatory companion signal (compensation alert) | 1 | defer | deferred |
| [0007](0007-weight-sensitivity-tooling.md) | Weight sensitivity tooling (OAT + simplex perturbation) | 2 | accept | accepted |
| [0008](0008-expose-cpr-latent-share.md) | Expose the CPR latent share as a parameter | 2 | accept | accepted |
| [0009](0009-tier-margin-reporting.md) | Tier margin reporting | 1 | defer | deferred |
| [0010](0010-close-health-equity-component.md) | Close (do not build) the health-equity component | 2 | accept | accepted |
| [0011](0011-guardrail-eligibility-and-cap-wording.md) | Guardrail eligibility and cap wording corrections | 2 | accept | accepted |
| [0012](0012-first-year-weight-rule-docs.md) | First-year weight-1 rule documentation | 1 | defer | deferred |
| [0013](0013-pin-reference-env-and-ci-matrix.md) | Pin reference environment and CI version matrix | 1 | defer | deferred |

**Cycle 1 report** (2026-07-11, evidence mode: web): 12 recommendations from 4 roles; 4
accepted (the batch cap), 8 deferred on cap/sequencing grounds — none rejected on merit.
Accepted batch: hazard-only composite (0002), log-symmetric EAV (0003), non-finite input
rejection (0004), golden-file oracles (0005). Fixture impact: BCS 0.4207 "moderate" →
0.502767 "high" (disclosed knife-edge margin 0.002767 above the boundary); contract
weighted index 0.322 → 0.3057. Deferred items 0006–0013 form cycle 2's opening agenda.

**Cycle 2 report** (2026-07-13, evidence mode: web): 8 deferred items from cycle 1
re-evaluated; 4 accepted (the batch cap), 4 remain deferred. Accepted batch: close
health-equity component (0010, doc-only), guardrail wording corrections (0011, doc-only),
expose CPR latent share (0008, code + 5 tests), weight sensitivity tooling (0007, new
module + script + 5 tests). Fixture unchanged (no formula/oracle value changes). Test
count: 85 → 95. Remaining deferred: 0006 (compensation alert), 0009 (tier margin),
0012 (first-year weight docs), 0013 (pin env/CI).

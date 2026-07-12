# 0013 — Reproducible reference environment: requires-python >=3.11, CI matrix 3.11–3.13, pinned constraints job

- **Status**: deferred
- **Cycle**: 1
- **Proposer**: stat-programmer
- **Component**: repro

## Context

The README claims a 'reproducible analytics framework', but `pandas>=2.0` floats with no lockfile, CI tests only Python 3.11, and pyproject claims >=3.9. Reproduced from scratch by three roles: Python 3.10 resolves pandas 2.3.3 while the CI lane runs pandas 3.0.3 — two majors under one spec, one tested. pandas 3.0 whatsnew (E1, verbatim): 'supports Python 3.11 and higher', default string dtype, copy-on-write. Skeptic's E1 (Python devguide): 3.9 is EOL since 2025-10-31, 3.10 EOL 2026-10 — the original matrix would have added CI for an unsupported interpreter absent from the dev box.

## Proposal (rebuttal-revised, breaking: true)

requires-python = '>=3.11' with migration note (3.9/3.10 installers get a clean pip refusal instead of a silently untested install); CI matrix ['3.11', '3.12', '3.13'] (3.11 and 3.13 lanes executed green this cycle, 60 passed each) plus a pinned reference job via new constraints.txt (pandas==3.0.3, numpy==2.4.6, pytest==9.1.1 — verified against the live environment); README reproducibility sentence points at constraints.txt.

## Decisive critique and verdict

**Defer** — cap-forced plus a deliberate sequencing choice: this cycle's batch is already breaking on methodology, and a packaging break will not be stacked on a formula break in one commit. The stake is real for the governance loop itself (this cycle's E3 evidence was computed on an unpinned environment), so as an interim control this cycle's QA records the execution environment (Python 3.11.15, pandas 3.0.3) in each accepted ADR's QA section. Next cycle: land the revised proposal as written; it also simplifies 0005's golden maintenance (single pandas major).

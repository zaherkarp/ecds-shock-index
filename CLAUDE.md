# ECDS Shock Index — agent notes

- Methodology changes (formulas, weights, parameters, tiers in
  `src/ecds_shock_index/__init__.py`) are governed by `docs/statistical-governance.md`:
  they require graded evidence, a team debate, an ADR in `docs/decisions/`, and atomic
  test-oracle updates derived from the ADR (not from running the new code).
- The statistician review team lives in `.claude/agents/stat-*.md`; orchestration
  workflows are `.claude/workflows/stat-team-cycle.js` (review→debate→verdict) and
  `.claude/workflows/stat-team-qa.js` (pre-commit QA gate).
- Run tests with `pytest` (install via `pip install -e ".[dev]"`).
- CMS/NCQA PDFs: WebFetch saves the binary locally; extract text with `pdftotext <path> -`.

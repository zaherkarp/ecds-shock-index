export const meta = {
  name: 'stat-team-qa',
  description: 'QA gate for an implemented statistician-team batch: independent programmer and skeptic verification, merged into pass/fail',
  whenToUse: 'Run AFTER implementing a stat-team-cycle batch and BEFORE committing it. args: {cycle_number, today (YYYY-MM-DD), adr_files: [paths], changed_files: [paths], baseline_dir?, evidence_mode?: "web"|"cached", repo_root?}. A "fail" gate blocks the batch commit.',
  phases: [
    { title: 'Verify', detail: 'programmer-verifier and skeptic-verifier run independently' },
  ],
}

const ROOT = (args && args.repo_root) || '/home/user/ecds-shock-index'
const CYCLE = args.cycle_number
const TODAY = args.today
const MODE = args.evidence_mode || 'web'
const ADRS = args.adr_files || []
const CHANGED = args.changed_files || []
const BASELINE = args.baseline_dir || '(no baseline dir provided — reconstruct the pre-batch behavior from git: `git stash` is NOT allowed; use `git show HEAD:<file>` to read pre-batch sources)'

const PROG_SCHEMA = {
  type: 'object',
  properties: {
    pytest: {
      type: 'object',
      properties: { pass: { type: 'boolean' }, summary: { type: 'string' } },
      required: ['pass', 'summary'],
    },
    cli: {
      type: 'object',
      properties: { pass: { type: 'boolean' }, summary: { type: 'string' } },
      required: ['pass', 'summary'],
    },
    notebook: {
      type: 'object',
      properties: { pass: { type: 'boolean' }, summary: { type: 'string' } },
      required: ['pass', 'summary'],
    },
    oracle_check: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          test: { type: 'string' },
          matches_adr: { type: 'boolean' },
          note: { type: 'string' },
        },
        required: ['test', 'matches_adr'],
      },
    },
    blocking_findings: { type: 'array', items: { type: 'string' } },
  },
  required: ['pytest', 'cli', 'notebook', 'oracle_check', 'blocking_findings'],
}

const SKEPTIC_SCHEMA = {
  type: 'object',
  properties: {
    derivations: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          adr: { type: 'string' },
          example: { type: 'string' },
          independent_result: { type: 'string' },
          matches: { type: 'boolean' },
        },
        required: ['adr', 'example', 'independent_result', 'matches'],
      },
    },
    citation_checks: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          adr: { type: 'string' },
          url: { type: 'string' },
          quote_found: { type: 'boolean' },
          note: { type: 'string' },
        },
        required: ['adr', 'url', 'quote_found'],
      },
    },
    behavior_diff: { type: 'string' },
    completeness: {
      type: 'object',
      properties: { pass: { type: 'boolean' }, gaps: { type: 'array', items: { type: 'string' } } },
      required: ['pass', 'gaps'],
    },
    verdict: { type: 'string', enum: ['pass', 'fail', 'pass-with-notes'] },
    blocking_findings: { type: 'array', items: { type: 'string' } },
  },
  required: ['derivations', 'citation_checks', 'behavior_diff', 'completeness', 'verdict', 'blocking_findings'],
}

const shared = [
  `Repository: ${ROOT}. Cycle ${CYCLE} batch has just been implemented in the working tree (NOT yet committed). Today: ${TODAY}. Evidence mode: ${MODE}.`,
  `Accepted ADRs for this batch: ${JSON.stringify(ADRS)}`,
  `Changed files: ${JSON.stringify(CHANGED)}`,
  `Pre-batch behavior baseline: ${BASELINE}`,
  `Governance: ${ROOT}/docs/statistical-governance.md. Your report gates the commit — be precise about what is blocking vs a note.`,
].join('\n')

phase('Verify')
log(`QA gate for cycle ${CYCLE}: ${ADRS.length} ADRs, ${CHANGED.length} changed files`)

const results = await parallel([
  () => agent([
    `Read ${ROOT}/.claude/agents/stat-programmer.md and fully adopt that role, acting as the batch VERIFIER.`,
    shared,
    `Verify the implemented batch:`,
    `1. Run the full test suite fresh: \`cd ${ROOT} && python -m pytest -q\`. Record pass/fail and the summary line.`,
    `2. CLI smoke: run single mode (pick factor values, hand-compute the expected composite from the CURRENT weights in src/ecds_shock_index/__init__.py, compare), batch mode against data/raw/example_*.csv (must run clean, check --json parses), and the legacy flat-arg mode.`,
    `3. Notebook: \`jupyter nbconvert --to notebook --execute ${ROOT}/notebooks/00-overview.ipynb --output /tmp/qa-notebook-out.ipynb\` — must exit 0. If the notebook prints stale numbers contradicting the new formulas, that is a blocking finding.`,
    `4. Oracle check: for each changed/added test expectation in the diff (git diff for tests/), confirm the expected value appears in (or derives from) the corresponding ADR's numerical-verification table. An oracle with no ADR derivation is a blocking finding.`,
  ].join('\n\n'), { label: 'qa:programmer', phase: 'Verify', schema: PROG_SCHEMA }),
  () => agent([
    `Read ${ROOT}/.claude/agents/stat-skeptic.md and fully adopt that role, acting in QA mode.`,
    shared,
    `Verify adversarially:`,
    `1. For EVERY accepted ADR: re-derive at least 2 numerical examples from the ADR's formula text with your own independent arithmetic (fresh python -c expressions or hand calculation — do NOT import the repo's code). Include clip/tier boundary points where relevant.`,
    `2. For EVERY accepted ADR: spot-check at least 1 citation (fetch it; PDFs via WebFetch then pdftotext). In cached mode, mark quote_found using the cached corpus and note it.`,
    `3. Behavior diff: score data/raw/example_*.csv with the NEW code (CLI batch mode) and diff against the baseline; attribute every delta to a specific ADR's impact claims. Unexplained drift = blocking.`,
    `4. Completeness: every src/ hunk in \`git diff\` maps to exactly one accepted ADR; every accepted ADR has verdict, rationale, evidence at/above the governance floor, and a filled numerical-verification table; docs/decisions/README.md index is current; docs/literature-evaluation.md has a summary row per accepted methodology change.`,
  ].join('\n\n'), { label: 'qa:skeptic', phase: 'Verify', schema: SKEPTIC_SCHEMA, effort: 'high' }),
])

const prog = results[0]
const skep = results[1]
const blocking = []
if (!prog) blocking.push('programmer-verifier agent failed to return a report')
else {
  if (!prog.pytest.pass) blocking.push(`pytest failed: ${prog.pytest.summary}`)
  if (!prog.cli.pass) blocking.push(`CLI smoke failed: ${prog.cli.summary}`)
  if (!prog.notebook.pass) blocking.push(`notebook execution failed: ${prog.notebook.summary}`)
  prog.oracle_check.forEach((o) => { if (!o.matches_adr) blocking.push(`oracle not derived from ADR: ${o.test}${o.note ? ' — ' + o.note : ''}`) })
  blocking.push(...prog.blocking_findings)
}
if (!skep) blocking.push('skeptic-verifier agent failed to return a report')
else {
  skep.derivations.forEach((d) => { if (!d.matches) blocking.push(`re-derivation mismatch (${d.adr}): ${d.example} → ${d.independent_result}`) })
  if (!skep.completeness.pass) blocking.push(`decision-log gaps: ${skep.completeness.gaps.join('; ')}`)
  if (skep.verdict === 'fail') blocking.push('skeptic verdict: fail')
  blocking.push(...skep.blocking_findings)
}

const gate = blocking.length === 0 ? 'pass' : 'fail'
log(`QA gate: ${gate}${blocking.length ? ` (${blocking.length} blocking finding(s))` : ''}`)
return { gate, blocking_findings: blocking, programmer_report: prog, skeptic_report: skep }

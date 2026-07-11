export const meta = {
  name: 'stat-team-cycle',
  description: 'One statistician-team cycle: independent reviews, cross-debate, rebuttals, referee verdict and batch plan',
  whenToUse: 'Run one evidence-gated methodology review cycle for the ECDS Shock Index. args: {cycle_number, today (YYYY-MM-DD), evidence_mode: "web"|"cached", decision_log_summary, focus_hint?, repo_root?}. Returns the referee verdict, batch plan, and ADR drafts; the caller implements the batch and then runs stat-team-qa.',
  phases: [
    { title: 'Review', detail: 'four reviewer roles propose up to 3 recommendations each' },
    { title: 'Debate', detail: 'peers and the skeptic critique every recommendation' },
    { title: 'Rebuttal', detail: 'proposers answer opposing critiques' },
    { title: 'Verdict', detail: 'referee accepts/rejects/defers and sequences the batch' },
  ],
}

const ROOT = (args && args.repo_root) || '/home/user/ecds-shock-index'
const CYCLE = args.cycle_number
const TODAY = args.today
const MODE = args.evidence_mode || 'web'
const LOG_SUMMARY = args.decision_log_summary || 'No prior decisions beyond ADR-0001 (framework adoption).'
const FOCUS = args.focus_hint ? `\nFocus hint from the maintainer (optional, not binding): ${args.focus_hint}` : ''

const REVIEW_ROLES = ['methodologist', 'calibration', 'domain-evidence', 'programmer']
const ROLE_TAG = { methodologist: 'METH', calibration: 'CAL', 'domain-evidence': 'DOM', programmer: 'PROG' }

const EVIDENCE_ITEM = {
  type: 'object',
  properties: {
    claim: { type: 'string' },
    grade: { type: 'string', enum: ['E1', 'E2', 'E3', 'E4'] },
    source: { type: 'string' },
    url: { type: 'string' },
    access_date: { type: 'string' },
    quote: { type: 'string' },
  },
  required: ['claim', 'grade', 'source', 'quote'],
}

const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    recommendations: {
      type: 'array',
      maxItems: 3,
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          title: { type: 'string' },
          component: { type: 'string', enum: ['ccs', 'eav', 'cpr', 'wm', 'composite', 'tiers', 'repro', 'other'] },
          problem: { type: 'string' },
          proposed_change: { type: 'string' },
          evidence: { type: 'array', items: EVIDENCE_ITEM },
          numerical_example: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                inputs: { type: 'string' },
                current_output: { type: 'string' },
                proposed_output: { type: 'string' },
              },
              required: ['inputs', 'current_output', 'proposed_output'],
            },
          },
          effort: { type: 'string', enum: ['S', 'M', 'L'] },
          breaking: { type: 'boolean' },
        },
        required: ['id', 'title', 'component', 'problem', 'proposed_change', 'evidence', 'numerical_example', 'effort', 'breaking'],
      },
    },
  },
  required: ['recommendations'],
}

const CRITIQUE_SCHEMA = {
  type: 'object',
  properties: {
    critiques: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          rec_id: { type: 'string' },
          critic_role: { type: 'string' },
          stance: { type: 'string', enum: ['support', 'oppose', 'amend'] },
          argument: { type: 'string' },
          counter_evidence: { type: 'array', items: EVIDENCE_ITEM },
          verification_attempted: { type: 'boolean' },
          verification_result: { type: 'string' },
        },
        required: ['rec_id', 'critic_role', 'stance', 'argument', 'verification_attempted', 'verification_result'],
      },
    },
  },
  required: ['critiques'],
}

const REBUTTAL_SCHEMA = {
  type: 'object',
  properties: {
    rebuttals: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          rec_id: { type: 'string' },
          rebuttal: { type: 'string' },
          concessions: { type: 'string' },
          revised_proposal: { type: 'string' },
        },
        required: ['rec_id', 'rebuttal', 'concessions'],
      },
    },
  },
  required: ['rebuttals'],
}

const REFEREE_SCHEMA = {
  type: 'object',
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          rec_id: { type: 'string' },
          verdict: { type: 'string', enum: ['accept', 'reject', 'defer'] },
          provisional: { type: 'boolean' },
          rationale: { type: 'string' },
          conditions: { type: 'string' },
        },
        required: ['rec_id', 'verdict', 'provisional', 'rationale'],
      },
    },
    batch_plan: {
      type: 'object',
      properties: {
        ordered_steps: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              step: { type: 'number' },
              rec_id: { type: 'string' },
              files: { type: 'array', items: { type: 'string' } },
              code_change_summary: { type: 'string' },
              test_changes: { type: 'string' },
              oracle_derivation: { type: 'string' },
            },
            required: ['step', 'rec_id', 'files', 'code_change_summary', 'test_changes', 'oracle_derivation'],
          },
        },
        estimated_loc: { type: 'number' },
        api_impact: { type: 'string', enum: ['none', 'additive', 'breaking-with-migration'] },
      },
      required: ['ordered_steps', 'estimated_loc', 'api_impact'],
    },
    adr_drafts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          rec_id: { type: 'string' },
          suggested_number_slug: { type: 'string' },
          markdown: { type: 'string' },
        },
        required: ['rec_id', 'suggested_number_slug', 'markdown'],
      },
    },
    cycle_summary: { type: 'string' },
  },
  required: ['verdicts', 'batch_plan', 'adr_drafts', 'cycle_summary'],
}

const commonContext = [
  `Repository: ${ROOT} (ECDS Shock Index).`,
  `Cycle number: ${CYCLE}. Today's date (use for access_date fields): ${TODAY}.`,
  `Evidence mode: ${MODE}. In "web" mode, fetch primary sources (HTML via WebFetch; for PDFs, WebFetch saves the binary to a local path shown in the result — extract with \`pdftotext <path> -\` in Bash). In "cached" mode, grade re-used citations E2 "cached, not re-verified".`,
  `First read ${ROOT}/docs/statistical-governance.md (evidence grades, acceptance floor, debate protocol).`,
  `Decision-log summary (do NOT re-litigate already-decided items; deferred items ARE on the agenda):\n${LOG_SUMMARY}`,
].join('\n')

const reviewPrompt = (role) => [
  `Read ${ROOT}/.claude/agents/stat-${role}.md and fully adopt that role, including its charter, boundaries, evidence rules, and output contract.`,
  commonContext,
  `Review the current state of the repository within your charter. Key material: src/ecds_shock_index/__init__.py, src/ecds_shock_index/data_loader.py, src/cli.py, tests/, docs/literature-evaluation.md, notebooks/00-overview.ipynb, README.md, data/raw/, .github/workflows/ci.yml (all under ${ROOT}).${FOCUS}`,
  `Produce your recommendations now (at most 3, ranked by importance, IDs C${CYCLE}-${ROLE_TAG[role] || role.toUpperCase()}-1..3). Every evidence entry must satisfy your evidence rules — fetch sources and run computations BEFORE writing the recommendation. If you have fewer than 3 defensible recommendations, return fewer; do not pad.`,
].join('\n\n')

phase('Review')
log(`Cycle ${CYCLE}: independent reviews by ${REVIEW_ROLES.length} statistician roles`)
const reviews = await parallel(REVIEW_ROLES.map((role) => () =>
  agent(reviewPrompt(role), { label: `review:${role}`, phase: 'Review', schema: REVIEW_SCHEMA })
))

const allRecs = []
reviews.forEach((r, i) => {
  const role = REVIEW_ROLES[i]
  if (!r) { log(`WARNING: review from ${role} was lost (agent error) — cycle continues without it`); return }
  r.recommendations.forEach((rec) => allRecs.push({ proposer: `stat-${role}`, ...rec }))
})
log(`${allRecs.length} recommendations entered debate`)
if (allRecs.length === 0) {
  return { recommendations: [], critiques: [], rebuttals: [], referee: null, note: 'No recommendations produced; nothing to debate.' }
}

const recsJson = JSON.stringify(allRecs, null, 1)

const critiquePrompt = (role, isSkeptic) => [
  `Read ${ROOT}/.claude/agents/stat-${role}.md and fully adopt that role.`,
  commonContext,
  `The team's recommendations for this cycle are below. ${isSkeptic ? 'Critique EVERY recommendation.' : `Critique every recommendation EXCEPT those proposed by your own role (proposer field = "stat-${role}").`} For each: take a stance (support/oppose/amend), argue from your charter, attach counter-evidence where you have it, and ATTEMPT VERIFICATION — re-derive at least one numerical example per recommendation you examine (independent arithmetic, not by trusting the proposer) and quote-check citations you have grounds to doubt. Record what you attempted and found in verification_result.`,
  `RECOMMENDATIONS:\n${recsJson}`,
].join('\n\n')

phase('Debate')
log('Cross-critique: 4 peer reviewers + skeptic')
const critiqueRoles = REVIEW_ROLES.concat(['skeptic'])
const critiqueResults = await parallel(critiqueRoles.map((role) => () =>
  agent(critiquePrompt(role, role === 'skeptic'), { label: `critique:${role}`, phase: 'Debate', schema: CRITIQUE_SCHEMA })
))
const allCritiques = critiqueResults.filter(Boolean).flatMap((c) => c.critiques)
log(`${allCritiques.length} critiques filed`)

const contested = {}
allCritiques.forEach((c) => {
  if (c.stance !== 'support') {
    const rec = allRecs.find((r) => r.id === c.rec_id)
    if (rec) {
      const role = rec.proposer.replace('stat-', '')
      if (!contested[role]) contested[role] = new Set()
      contested[role].add(c.rec_id)
    }
  }
})

const rebuttalPrompt = (role, recIds) => {
  const own = allRecs.filter((r) => recIds.has(r.id))
  const crits = allCritiques.filter((c) => recIds.has(c.rec_id) && c.stance !== 'support')
  return [
    `Read ${ROOT}/.claude/agents/stat-${role}.md and fully adopt that role.`,
    commonContext,
    `Your recommendations below received opposing or amending critiques. You get ONE rebuttal per recommendation: answer the critiques directly, concede what is right (concessions), and if a critique improves the proposal, state a revised_proposal. Run new computations or fetches if they settle a disputed point.`,
    `YOUR RECOMMENDATIONS:\n${JSON.stringify(own, null, 1)}`,
    `CRITIQUES TO ANSWER:\n${JSON.stringify(crits, null, 1)}`,
  ].join('\n\n')
}

phase('Rebuttal')
const contestedRoles = Object.keys(contested)
log(contestedRoles.length ? `Rebuttals from: ${contestedRoles.join(', ')}` : 'No opposed/amended recommendations — skipping rebuttals')
const rebuttalResults = contestedRoles.length
  ? await parallel(contestedRoles.map((role) => () =>
      agent(rebuttalPrompt(role, contested[role]), { label: `rebuttal:${role}`, phase: 'Rebuttal', schema: REBUTTAL_SCHEMA })
    ))
  : []
const allRebuttals = rebuttalResults.filter(Boolean).flatMap((r) => r.rebuttals)

phase('Verdict')
log('Referee: verdicts, batch plan, ADR drafts')
const referee = await agent([
  `Read ${ROOT}/.claude/agents/stat-referee.md and fully adopt that role, including the hard caps and evidence floor you enforce.`,
  commonContext,
  `Also read ${ROOT}/docs/decisions/TEMPLATE.md — accepted ADR drafts must follow it (rejected/deferred may use the short form). ADR numbering starts AFTER the highest number currently in ${ROOT}/docs/decisions/ (check it).`,
  `Judge the full debate record below. Produce verdicts for every recommendation, the sequenced batch plan for accepted items (with oracle derivations computed from formula text — show arithmetic), ADR drafts for ALL items, and the cycle summary.`,
  `RECOMMENDATIONS:\n${recsJson}`,
  `CRITIQUES:\n${JSON.stringify(allCritiques, null, 1)}`,
  `REBUTTALS:\n${JSON.stringify(allRebuttals, null, 1)}`,
].join('\n\n'), { label: 'referee', phase: 'Verdict', schema: REFEREE_SCHEMA, effort: 'high' })

if (referee) {
  const counts = { accept: 0, reject: 0, defer: 0 }
  referee.verdicts.forEach((v) => { counts[v.verdict] = (counts[v.verdict] || 0) + 1 })
  log(`Verdicts: ${counts.accept} accepted, ${counts.reject} rejected, ${counts.defer} deferred`)
}

return { recommendations: allRecs, critiques: allCritiques, rebuttals: allRebuttals, referee }

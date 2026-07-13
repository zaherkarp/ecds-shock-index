# 0010 — EHO4all (formerly HEI) reward not implemented for 2027 Star Ratings: close the health-equity component without build

- **Status**: accepted
- **Cycle**: 2 (deferred cycle 1, accepted cycle 2)
- **Proposer**: stat-domain-evidence
- **Component**: composite

## Context

Two locations carried the stale premise that the Health Equity Index is replacing the reward factor: `docs/literature-evaluation.md` (future-work bullet) and `.claude/agents/stat-domain-evidence.md` (charter text). The CY2027 final rule fact sheet (CMS-4208-F3/CMS-4212-F, April 2, 2026) states CMS is NOT implementing the Excellent Health Outcomes for All reward for the 2027 Star Ratings and continues the historical reward factor. The 2026 Technical Notes still compute the historical r-Factor (Tables 8/9). Closing without build protects the accepted 3-hazard composite (ADR-0002) from an unevidenced fifth-component re-normalization.

## Proposal

Documentation and decision-log only. (1) Replace `literature-evaluation.md` future-work bullet with closure statement citing CMS-4208-F3/CMS-4212-F. (2) Replace `stat-domain-evidence.md` charter text with closure statement and re-open trigger. (3) Flip ADR-0010 status deferred→accepted. Retain rulemaking-reversal trail (HEI→EHO4all→not implemented) in the ADR body. No code, schema, weight, or oracle change.

## Evidence

| Claim | Grade | Source | URL | Accessed | Supporting quote |
|---|---|---|---|---|---|
| CMS is not implementing EHO4all for 2027 | E1 | CMS CY2027 final rule fact sheet (CMS-4208-F3/CMS-4212-F) | https://www.cms.gov/newsroom/fact-sheets/contract-year-2027-medicare-advantage-part-d-final-rule | 2026-07-13 | 'CMS is not implementing the Excellent Health Outcomes for All reward (previously called the Health Equity Index reward)' |
| CMS continues the historical reward factor | E1 | CMS CY2027 final rule fact sheet | https://www.cms.gov/newsroom/fact-sheets/contract-year-2027-medicare-advantage-part-d-final-rule | 2026-07-13 | 'will continue the historical reward factor that encourages consistently high performance for all enrollees across all quality measures' |
| 2026 Technical Notes still compute historical r-Factor | E1 | CMS 2026 Star Ratings Technical Notes | https://www.cms.gov/files/document/2026-star-ratings-technical-notes.pdf | 2026-07-13 | 'Applying the Reward Factor' section with Tables 8/9 |

## Numerical verification

| Inputs | Old output | New output | Derivation |
|---|---|---|---|
| Fixture batch | COL 0.119576 low, BCS 0.502767 high, A1C 0.302032 moderate, contract 0.3057 | identical | Doc-only change; no fifth component added |

## Verdict

Accepted. Live E1 discharges the cycle-1 re-fetch condition. CMS is not implementing EHO4all for 2027; historical reward factor continues. Zero code risk. Re-open only if CMS finalizes an implementation year.

## QA result

Pending (cycle-2 QA gate).

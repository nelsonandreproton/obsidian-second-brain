---
type: knowledge-proposal
triggered-by: {{knowledge/sources/slug}}
date: {{date}}
affects: {{SKILL.md | templates | patterns | project approach}}
status: pending
---

# Proposal: {{Short Title}}

[[knowledge/index]]

**Triggered by:** [[knowledge/sources/{{source-slug}}]]
**Date:** {{date}}
**Affects:** {{what this would change}}
**Status:** `pending` → change to `accepted`, `rejected`, or `modified` after review

---

## Current Approach

{{Describe exactly what we currently do — quote from SKILL.md, patterns, or project notes
if relevant. Be specific so the comparison is fair.}}

## Suggested Improvement

{{What the source recommends instead. Stay close to the source's actual suggestion —
don't over-interpret.}}

## Rationale

{{Why this might be better. Ground it in the source and in the user's goals from me.md.
Note any trade-offs or risks.}}

## How to Implement

{{Specific steps to apply this if accepted:
- Which files to edit
- What to add/change/remove
- Any migration needed for existing vault data}}

## Decision

- [ ] Accept — implement as described
- [ ] Reject — reason: {{reason}}
- [ ] Modify — adjusted version: {{description}}

**Decision date:** {{date when decided}}
**Notes:** {{free text}}

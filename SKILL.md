---
name: obsidian-second-brain
description: >
  Maintains a persistent "second brain" in Obsidian for Claude Code, so Claude never starts
  from scratch on known projects. Use this skill whenever the user is working on a project
  that should have memory, asks Claude to remember or update project context, starts a new
  session on an existing project, runs `init`, `sync`, `load context`, or `inspect`,
  wants to add a new project to the knowledge base, says "add project X", or asks "what do you know about X project".
  Also triggers automatically when a CLAUDE.md file references an Obsidian vault path.
  ALSO triggers on first-time phrases like "setup second brain", "configure vault",
  "where is my obsidian", or any mention of setting up project memory for the first time.
  Commands: setup, init, sync, context, log, inspect.
---

# Obsidian Second Brain

Persistent project memory for Claude Code via an Obsidian vault. Claude reads and writes
structured Markdown notes so every session starts with full context — no re-explaining needed.
The Obsidian graph view acts as the visual knowledge graph: wikilinks between notes are the edges.

---

## Core Concepts

- **Vault** — the Obsidian folder that stores all knowledge (`obsidian_vault_path` in config)
- **system.md** — master index: all projects, patterns, key decisions
- **projects/<n>/<n>.md** — per-project details, stack, links, status (loaded as context)
- **projects/<n>/<n>-history.md** — session changelog (what changed, when, by whom)
- **projects/<n>/<n>-spec.md** — technical specification: APIs, data models, env vars, deployment (documentation only — NOT loaded as context)
- **patterns/** — reusable knowledge across projects (stack, architecture decisions)
- **amendments/** — proposed skill patches with rationale and evaluation results
- **history/YYYY-MM-DD.md** — daily cross-project changelog: one file per day, aggregates all project history entries for that day
- **logs/skill_runs.csv** — audit trail of every skill action (feeds the Inspect loop)

---

## Step 0 — `setup` (run once, never again)

**When:** The very first time. Triggered by: "setup second brain", "configure vault",
"where is my obsidian", "init for the first time", or when `config.yaml` does not exist
anywhere on the system.

This is a guided wizard — ask questions one at a time, confirm before writing anything.

### Wizard flow

**Question 1 — Vault location**
```
Where is your Obsidian vault?
Example: ~/Documents/ObsidianVault or /Users/nelson/Obsidian/Brain

> _
```
- Accept `~` paths and expand them
- Check the path exists. If not: "That folder doesn't exist yet. Create it? (yes/no)"
- If the folder exists but has no `.obsidian/` subfolder: warn "This doesn't look like an
  Obsidian vault — it has no .obsidian/ folder. Continue anyway? (yes/no)"

**Question 2 — Project source folders**
```
Which folders contain your projects? (one per line, blank line to finish)
Example:
  ~/projects
  ~/docker
  /opt/services

> _
```
- Accept multiple paths, expand `~`
- For each path: verify it exists, list how many immediate subdirectories were found
- Show the candidate project list: "Found 5 candidate projects: GarminBot, cncSearch, ..."
- Ask: "Exclude any? (comma-separated names, or press Enter to keep all)"

**Question 3 — Confirm and write**
```
Ready to create:
  Vault:    ~/Documents/ObsidianVault
  Projects: ~/projects, ~/docker
  Will scan: GarminBot, cncSearch, jmj2027, hetznercheck, homeserver

Write config.yaml and run init? (yes/no)
```

Only after "yes": write `config.yaml`, then run the full `init` flow automatically.

**After setup completes**, print:
```
✅ Second brain ready.

Next time, just say:
  "load context"   → loads memory for the current project
  "sync project"   → updates notes after you make changes
  "log session"    → saves what we did today
  "inspect skill"  → checks for recurring failures and suggests improvements
```

---

## Configuration

`config.yaml` lives at `{obsidian_vault_path}/config.yaml`. Created by `setup`, never
edited manually unless the user asks.

```yaml
obsidian_vault_path: ~/Documents/ObsidianVault
projects_folder: projects
templates_folder: templates
patterns_folder: patterns
amendments_folder: amendments
logs_folder: logs
raw_folder: raw                     # immutable source documents (never modified by Claude)
knowledge_folder: knowledge         # LLM-generated wiki from ingested sources
me_file: me.md                      # personal context loaded during every ingest
system_file: system.md
skill_version: 1                    # incremented on each accepted amendment
stale_threshold_days: 7             # warn when project is newer than notes by this many days

project_sources:
  - ~/projects
  - ~/docker

scan_targets:
  - README.md
  - docker-compose.yml
  - Dockerfile
  - .env.example
  - package.json
  - requirements.txt
  - pyproject.toml
  - go.mod
  - Makefile

scan_max_lines: 80

scan_ignore:
  - node_modules
  - .git
  - dist
  - build
  - __pycache__

inspect_failure_threshold: 3       # trigger inspect suggestion after N failures on same command
log_file: log.md                    # human-readable append-only activity log (Obsidian-visible)
lint_auto_interval: 10              # suggest lint after every N log/sync calls (checked via log.md count)
log_queries: false              # set to true to log [QUERY] entries for every context load (can be verbose)
```

Expand `~` to actual home path. Fail loudly if `obsidian_vault_path` doesn't exist.

### Finding config.yaml

Before any command can run, the vault path must be resolved. Use this order:

1. **CLAUDE.md in cwd** — look for `obsidian_vault:` field in `CLAUDE.md` of the current working directory → read `{vault}/config.yaml`
2. **CLAUDE.md walk-up** — if not in cwd, check parent directories up to 3 levels
3. **Known locations** — try `~/Documents/ObsidianVault/config.yaml`, `~/Obsidian/config.yaml`, `~/Documents/Obsidian/config.yaml`
4. **Fail loudly** — if still not found, stop and tell the user: "Could not find config.yaml. Add `obsidian_vault: /path/to/vault` to a CLAUDE.md file in your project folder, or run `setup second brain`."

Never silently fall back to a default path.

---

## Vault Structure

```
{vault}/
  config.yaml
  system.md
  projects/
    GarminBot/
      GarminBot.md                        ← context note (loaded by `context` command)
      GarminBot-history.md                ← session changelog
      GarminBot-spec.md                   ← technical spec (documentation only, not loaded as context)
      GarminBot-lessons-learned.md        ← accumulated lessons: bugs, gotchas, decisions worth remembering
    CNCSearch/
      CNCSearch.md
      CNCSearch-history.md
      CNCSearch-spec.md
      CNCSearch-lessons-learned.md
  history/
    2026-03-21.md              ← daily cross-project changelog
    2026-03-22.md
  patterns/
    stack.md
    decisions.md
  amendments/
    SKILL_v1_patch.md
    SKILL_v2_patch.md
  SKILL.v1.md                  ← snapshot before each accepted amendment
  SKILL.v2.md
  templates/
    project_template.md
    spec_template.md
    system_template.md
    history_template.md
    history_daily_template.md
    lessons_learned_template.md
    amendment_template.md
  logs/
    skill_runs.csv          ← machine-readable audit trail (feeds inspect)
    log.md                  ← human-readable append-only activity log (visible in Obsidian graph)
  raw/                      ← immutable source documents (never modified by Claude)
    article-karpathy.md
    transcript-foo.md
    ...
  knowledge/                ← LLM-generated wiki from ingested sources
    index.md                ← catalog of all knowledge pages
    sources/                ← one summary page per ingested document
      karpathy-llm-wiki.md
    topics/                 ← concept pages (one per theme/technology/pattern)
      agentic-workflows.md
      context-management.md
    proposals/              ← improvement proposals for human review (never auto-applied)
      improve-skill-ingest.md
  me.md                     ← personal context: goals, strengths, style, setup
```

---

## Commands

### 1. `init` — Bootstrap the vault

**When:** After `setup`, or explicitly "init vault" / "rebuild second brain".

**Steps:**
1. Read `config.yaml` (must exist — if not, run `setup` first)
2. Create vault folder structure above (including `history/`)
3. Copy templates from `assets/templates/` if not already present
4. For each path in `project_sources`: scan subdirectories as candidate projects
5. For each candidate: run **scan routine**
6. Create or update `system.md`
7. Log to CSV

**Scan routine** (per project folder):
1. **Migration check:** if old `projects/<n>/project.md` exists but `projects/<n>/<n>.md` does not → rename `project.md` → `<n>.md` and `history.md` → `<n>-history.md` automatically, report the rename
2. Skip if `projects/<n>/<n>.md` already exists and `--force` not set
3. Read `scan_targets` in order — stop after 3 found, max `scan_max_lines` each
4. Extract: name, purpose (1–2 sentences), tech stack, services/ports, URLs
5. Fill `project_template.md` → write `projects/<n>/<n>.md`
6. Write `projects/<n>/<n>-history.md` from `history_template.md`
7. Write `projects/<n>/<n>-spec.md` from `spec_template.md` — populate with env vars, ports, data models, deployment notes extracted from scan files
8. Add `[[projects/Name/Name]]` wikilink to `system.md` projects table
   (this wikilink is the graph edge — essential for Obsidian graph view)

**`system.md` format** — a content-oriented catalog, not just a list. Rebuild fully on
`init`, update incrementally on `sync` and `log`:

```markdown
# Second Brain — System Index

[[logs/log]] | [[patterns/stack]] | [[patterns/decisions]]

## By Stack
Group projects under their primary stack/runtime. Update groupings on sync.

### Python
- [[projects/GarminBot/GarminBot]] — Garmin health data → Telegram bot
- [[projects/cncSearch/cncSearch]] — CNC machine parts search API

### Docker / Infrastructure
- [[projects/homeserver/homeserver]] — Home lab Docker stack

## All Projects

| Project | Stack | Status | Last sync |
|---------|-------|--------|-----------|
| [[projects/GarminBot/GarminBot\|GarminBot]] | Python, Docker | active | 2026-04-07 |

## Patterns
- [[patterns/stack]] — shared stack conventions across projects
- [[patterns/decisions]] — architectural decisions log

## Amendments
- [[amendments/SKILL_v2_patch]] — lessons-learned system (accepted)
```

Rules:
- Keep the "By Stack" section grouped — reassign projects when their stack changes
- Update the "Last sync" date on every `sync` and `log` call for that project
- The wikilinks in every section are the graph edges — never omit them

**CLAUDE.md bridge:** After init, create a `CLAUDE.md` in each project folder (skip if one already exists):
```markdown
# Claude Code Context
obsidian_vault: {obsidian_vault_path}
project: {ProjectName}
Run: `load context` to initialise session memory.
```
This file is how the skill finds the vault when invoked from a project directory.

---

### 2. `sync` — Update a project after changes

**When:** "sync project", "update context for X", "I made changes to X", "add project X", or when a project folder exists on disk but has no notes in the vault yet.

**Steps:**
1. Identify project (from cwd, explicit name, or ask)
2. Re-run scan routine on that project folder
3. **Git context** — run in the project directory:
   - `git log --oneline -10` → recent commits since last sync (use to enrich the diff summary)
   - `git status --short` → current state
   - `git branch --show-current` → active branch
   - `git diff --stat HEAD` → files changed since last commit
4. Show diff: what changed (2–3 lines max), enriched with recent commits
5. Append to `projects/<n>/<n>-history.md`:
   ```markdown
   ## {ISO date} — Sync
   - Updated: {changed fields}
   - Notes: {brief summary}
   ```
6. Update `projects/<n>/<n>-spec.md` if env vars, ports, or data models changed
7. Update `system.md` entry if status or description changed
8. Check for `CLAUDE.md` in the project folder — create it if missing (same format as init bridge)
9. **Lessons learned** — propose candidates, then write confirmed ones (see **Lessons Learned** below)
10. **Cross-project patterns** — after lessons are confirmed, scan all other `projects/*/<n>.md`
    files for matching `stack:` entries. If ≥ 2 other projects share the same stack component
    involved in a confirmed lesson, propose: *"This lesson may apply to [ProjectX, ProjectY]
    (same stack component). Add a cross-reference to `patterns/stack.md`? (yes/skip)"*
    Present the proposal before writing anything. Wait for confirmation.
11. Update `history/{ISO date}.md` — append project section (see **Daily History** below)
12. Append `[INGEST]` entry to `logs/log.md` (see **Logging** below; create file with `# Activity Log` header if not yet present)
13. Log to CSV
14. **Lint nudge** — count `[INGEST]` + `[SESSION]` entries in `log.md`; if the count is a
    multiple of `lint_auto_interval`, append at end of response: *"Vault health check due —
    run `lint vault`?"*

---

### 3. `context` — Load context for current session

**When:** Starting work, "load context", "what do you know about X", or CLAUDE.md present.
This is the **most used command** — keep it fast and lean.

**Steps:**
1. **Pending failure check** — silently scan `logs/skill_runs.csv` for any command with
   failures ≥ `inspect_failure_threshold`. For each such command, check `amendments/`
   for any file containing the string `command \`{command}\`` in its "Triggered by:" line —
   if found, treat that command as already addressed and skip it. Surface a nudge only for
   unaddressed commands, at the very end of the Context Summary; do not interrupt loading.
2. Identify project (cwd name → known projects, or ask)
3. **Stale check** — compare the file modification time of `projects/<n>/<n>.md` against
   the most recently modified scan target file in the project directory (use `stat` or
   equivalent). If the project source file is newer than the vault note by more than
   `stale_threshold_days`, flag it — append after the Context Summary:
   *"⚠️ Notes are X days old — project was modified more recently. Sync first? (yes/skip)"*
   Do not block loading; always output the Context Summary first.
4. **Intent detection** — parse the user's current message (or session opener) to decide
   what extra files to load beyond the defaults:
   - Bug / error / failing / traceback / exception → also load `projects/<n>/<n>-lessons-learned.md`
   - Architecture / design / refactor / spec / model → also load `projects/<n>/<n>-spec.md`
   - Names another known project → also load that project's `<n>.md` (one level only —
     do not recursively load projects mentioned within the loaded notes)
   - AI engineering / prompting / agentic / context / Claude Code topic → also load
     matching `knowledge/topics/*.md` pages and `me.md`
   - Default: load only the files listed in steps 5–7 below
5. Read `system.md` patterns section + project entry
6. Read `projects/<n>/<n>.md`
7. Read last 3 entries from `projects/<n>/<n>-history.md`
8. Read `patterns/stack.md` and `patterns/decisions.md`
9. **Git context** — run in the project directory:
   - `git log --oneline -10` → recent commits
   - `git status --short` → current state
   - `git branch --show-current` → active branch
   - `git diff --stat HEAD` → files changed since last commit
10. Output **Context Summary** (format below)
11. Append `[QUERY]` entry to `logs/log.md` only if `log_queries: true` in config (see **Logging** below; create file with `# Activity Log` header if not yet present)
12. Log to CSV

**Context Summary:**
```
## 🧠 Context Loaded: {ProjectName}

**Purpose:** {one sentence}
**Stack:** {comma list}
**Key services:** {ports/services}
**Branch:** {current branch} | **Last commit:** {hash} {message}
**Recent work:** {last 3 commits, one line each}
**Currently changed:** {git status summary, or "clean" if nothing}
**Last session:** {date} — {one line summary}
**Patterns active:** {relevant patterns}
**Open items:** {TODOs from <n>.md}

Ready. What are we working on?
```

If pending failures were found in step 1, append:
```
---
⚠️ {N} `{command}` failures logged since last inspect — run `inspect skill`?
```

---

### 4. `log` — Record a session note

**When:** "log this session", "save what we did", "log and sync", "sync and log",
end of work session.

**Combined trigger:** If the phrase matches both `log` and `sync` intent (e.g. "log and
sync to second brain"), run `log` first, then `sync` automatically in sequence — no second
prompt needed. Report both actions in a single summary response. When running as combined trigger, skip the cross-project pattern check in `sync` (step 10) — it will be covered by `log` step 7.

**Steps:**
1. Infer from conversation (or ask): what was done, any open items, any new patterns
2. **Check for existing session file** (`~/.claude/session-data/YYYY-MM-DD-*-session.tmp`):
   if one exists, read it before writing — the ECC system may have pre-created it and the
   Write tool requires a prior read. Enrich the existing file rather than creating a new one.
3. Append entry to `projects/<n>/<n>-history.md`
4. If new pattern emerged, offer to add to `patterns/`
5. Update `system.md` last-updated date
6. **Lessons learned** — propose candidates, then write confirmed ones (see **Lessons Learned** below)
7. **Cross-project patterns** — after lessons are confirmed, scan all other `projects/*/<n>.md`
   files for matching `stack:` entries. If ≥ 2 other projects share the same stack component
   involved in a confirmed lesson, propose: *"This lesson may apply to [ProjectX, ProjectY]
   (same stack component). Add a cross-reference to `patterns/stack.md`? (yes/skip)"*
   Present the proposal before writing anything. Wait for confirmation.
8. **Store synthesis** — review the conversation for any valuable output beyond lessons:
   architectural decisions, reusable design patterns, conceptual breakthroughs, or
   non-obvious solutions. If found, propose:
   *"This session produced [X]. File to vault? (yes: patterns/decisions / yes: patterns/stack /
   yes: new page in patterns/ / skip)"*
   Wait for confirmation before writing. Keep entries actionable and specific.
9. **Periodic patterns synthesis** — count `[SESSION]` entries in `log.md`; every 5th entry,
   run all three passes below. Present them together in one block — don't ask three times.

   **Pass A — Cross-project themes:** scan ALL `*-lessons-learned.md` files for themes
   mentioned ≥ 3 times across different projects (same library, same error type, same
   architectural pattern). Propose consolidating recurring themes into `patterns/stack.md`
   or `patterns/decisions.md`.

   **Pass B — `me.md` evolution:** read `me.md` and compare against recent sessions.
   Look for:
   - New tools or technologies used that aren't listed in the **Setup** section
   - Skills demonstrated repeatedly that could graduate from **Areas to Develop** to **Strengths**
   - Goals that appear complete or have shifted in priority
   - Working-style observations (e.g. consistently preferring a certain debugging approach)

   **Pass C — Knowledge gap proposals:** scan `knowledge/topics/` for any topic where the
   **Evolution** section has no entries added in the past 30 days, yet related work appeared
   in recent sessions. Propose: *"Topic [X] may need updating — you've worked on [related
   area] recently. Refresh it? (yes/skip)"*

   Present all proposals together:
   ```
   Periodic synthesis (every 5th session):

   Patterns: [theme] appears in ProjectA, ProjectB, ProjectC — consolidate to patterns/?
   me.md: You've used [tool] in 3 sessions — add to Setup? / [skill] could move from
           Areas to Develop → Strengths?
   Knowledge: [topic] page hasn't been updated in 35 days — refresh?

   Apply any? (1/2/3 / all / skip)
   ```
   Wait for confirmation before writing anything.
10. Update `history/{ISO date}.md` — append project section (see **Daily History** below)
11. Append `[SESSION]` entry to `logs/log.md` (see **Logging** below; create file with `# Activity Log` header if not yet present)
12. Log to CSV
13. **Lint nudge** — same check as in `sync` step 14.

---

### 5. `inspect` — Analyse failures and propose amendment

**When:** "inspect skill", "why does X keep failing", or automatically triggered when
`skill_runs.csv` accumulates ≥ `inspect_failure_threshold` failures for the same command.

**Steps:**
1. Read `logs/skill_runs.csv` — filter `success=false`
2. Group by `command` + `error_notes` — find recurring patterns
3. Cross-reference with `amendments/` — skip issues already addressed
4. Read the affected section of the current `SKILL.md`
5. Write amendment proposal to `amendments/SKILL_v{N}_patch.md` (format below)
6. Show proposal and ask: "Apply this amendment? (yes / no / modify)"

**If yes:**
  - Save current SKILL.md snapshot as `SKILL.v{current_version}.md` in vault root
  - Apply the patch to SKILL.md
  - Increment `skill_version` in `config.yaml`
  - Append evaluation result to the amendment file
  - Log to CSV with `project=_skill`

**If no:** Log decision, keep amendment file for future reference (visible in Obsidian graph).

**Either way:** Append `[AMEND]` entry to `logs/log.md`. Log to CSV with `project=_skill`.

**Amendment file format** (`amendments/SKILL_v{N}_patch.md`):
```markdown
# Amendment v{N} — {short title}

**Date:** {ISO date}
**Triggered by:** {N} failures on command `{command}`
**Linked runs:** [[logs/skill_runs]]
**Affected projects:** [[ProjectName]]

## Problem
{what kept failing and why, with specific error_notes values from CSV}

## Proposed change
**Section:** {section name in SKILL.md}

**Before:**
{old text, verbatim}

**After:**
{new text}

## Rationale
{why this change should fix it, grounded in observed failures}

## Evaluation
- Applied: {ISO date or "pending"}
- Result: {improved / no change / reverted}
- Notes: {free text}
```

The `[[ProjectName]]` and `[[logs/skill_runs]]` wikilinks make this amendment node visible
in the Obsidian graph, connecting it to the projects that triggered it.

---

### 6. `lint` — Vault health check

**When:** "lint vault", "check vault health", "find orphan pages", "check for broken links",
or automatically suggested when `log.md` entry count reaches a multiple of `lint_auto_interval`.

**Steps:**
1. **Broken wikilinks** — scan all vault `.md` files for `[[...]]` patterns; verify each
   target path resolves to an existing file. List broken links with their source file.
2. **Orphan pages** — find `.md` files in `projects/` and `patterns/` with no inbound
   wikilinks from any other vault file. These are candidates for archiving or reconnecting.
3. **Stale notes** — run the stale check (file mtime comparison) for ALL tracked projects
   at once, not just the current one. List every project overdue for sync.
4. **Missing CLAUDE.md bridges** — list project folders in `project_sources` that exist on
   disk but have no `CLAUDE.md` file.
5. **Spec contradictions** — for each project, compare the `stack:` field in `<n>.md`
   against the tech stack mentioned in `<n>-spec.md`. Flag mismatches.
6. **Output lint report:**
   ```
   ## 🔍 Vault Lint Report — {ISO date}

   **Broken links:** {N} — {list}
   **Orphan pages:** {N} — {list}
   **Stale notes:** {N} — {list with days overdue}
   **Missing CLAUDE.md:** {N} — {list}
   **Spec contradictions:** {N} — {list}
   ```
7. Ask: "Auto-fix what's possible? (yes/skip)"

**Auto-fixable (with confirmation):** Missing CLAUDE.md bridges (create them using init
bridge format). Orphan pages that have a matching project — add the missing wikilink.

**Manual only:** Broken links (target file may need creating or link needs correcting),
spec contradictions (requires human judgement on which version is correct).

8. Append `[LINT]` entry to `logs/log.md` (see **Logging** below). Log to CSV.

---

### 7. `ingest` — Process a raw source into the knowledge wiki

**When:** "ingest [file]", "process this document", "add this to my knowledge base",
"analyse this article", or when a file is dropped into the `raw/` folder.

**Philosophy:** One source at a time. Claude reads and thinks; you guide what to emphasise.
The raw file is never modified. All output lives in `knowledge/`. Nothing is auto-applied
to existing project notes or SKILL.md — improvements go into `knowledge/proposals/` for
human review and deliberate implementation.

**Steps:**

1. **Identify and convert source**
   - Accept: path to file in `raw/`, pasted markdown, or file reference (preferred)
   - URLs are accepted but require explicit confirmation before fetching: "Fetch `{url}`? This will make a network request. (yes/no)"
   - If PDF → extract text to markdown; if URL → fetch and convert only after confirmation; if image → describe
   - Confirm format with user before proceeding

2. **Load context**
   - Read `me.md` → personal goals, strengths, projects, style
   - Read `knowledge/index.md` → existing knowledge (avoid duplication, find connections); if not present, create it from `knowledge_index_template.md` before reading
   - Read `patterns/stack.md` and `patterns/decisions.md` → current approaches to challenge

3. **Discuss with user**
   Present a structured brief:
   ```
   ## Source brief: {title}
   **Type:** {article / transcript / note / paper}
   **Core thesis:** {1–2 sentences}
   **Relevance to you:** {filtered through me.md — why this matters for your work}
   **Key sections:** {list}

   What would you like me to emphasise? Any sections to skip?
   ```
   Wait for guidance before writing anything.

4. **Create source summary page** → `knowledge/sources/{slug}.md`
   Use `knowledge_source_template.md`. Include:
   - Summary (3–5 paragraphs)
   - Key takeaways (bulleted, actionable)
   - Connections to current projects (wikilinks)
   - What this challenges in current approach

5. **Update or create topic pages** → `knowledge/topics/{topic}.md`
   For each significant concept in the source:
   - If page exists: append new insights and add source to its Sources section
   - If new: create from `knowledge_topic_template.md`
   - Link topic pages to each other and to relevant project notes

6. **Challenge existing approach**
   Compare insights against `patterns/`, `SKILL.md`, and project approaches.
   For each genuine improvement identified:
   - Create `knowledge/proposals/{slug}.md` from `knowledge_proposal_template.md`
   - Include: current approach, suggested change, rationale, how to implement if accepted
   - Do NOT modify anything — proposals are read-only suggestions

7. **Update knowledge/index.md**
   Add the new source and any new topic pages to the catalog.
   Update the "Last ingested" date.

8. **Append `[KNOWLEDGE]` entry to `logs/log.md`**. Log to CSV with `project=_knowledge`.

**`me.md` usage during ingest:**
- Filter insights: prioritise content relevant to the user's stated goals and projects
- Personalise connections: "This applies to GarminBot because..."
- Calibrate depth: match the user's current skill level — don't over-explain known concepts
- Challenge constructively: flag gaps between the source's best practices and current work

> **Privacy note:** `me.md` may contain sensitive personal context. If your vault is stored in a public git repository, add `me.md` to `.gitignore` or keep only non-sensitive content in it.

---

### 8. `weekly` — Weekly synthesis

**When:** "weekly review", "how was my week", "weekly synthesis", "what did I work on this week",
or "weekly recap".

**Steps:**

1. **Determine the week** — default to the most recent completed Monday–Sunday range.
   If today is Monday, default to last week. Accept explicit overrides: "week of Apr 7" or "last week".

2. **Collect daily files** — read every `history/YYYY-MM-DD.md` in the date range.
   If no files exist for the range, report: "No history found for that week." and stop.

3. **Read `me.md`** → current goals and areas to develop.

4. **Aggregate per project:**
   - What was done (from daily history entries)
   - Lessons learned (from `**Lessons:**` lines in daily files)
   - Open items still pending (not checked off in `<n>.md`)

5. **Identify cross-project themes** — concepts or patterns that appeared in ≥ 2 projects
   during the week (same library, same type of work, same class of problem).

6. **Map to goals** — for each goal in `me.md`, identify which work this week moved it forward.
   If a goal had zero activity, flag it as "no progress this week".

7. **Surface stalled items** — scan all `projects/<n>/<n>.md` open items;
   flag any not mentioned in this week's history.

8. **Write `weekly/YYYY-WXX.md`** using `weekly_template.md`.
   Create `weekly/` folder if it doesn't exist.
   Add `[[weekly/YYYY-WXX]]` wikilink to `system.md` under a `## Weekly Reviews` section
   (create the section if absent).

9. **Log to CSV** with `project=_weekly`.

**Output after writing:**
```
## Week YYYY-WXX ({Mon DD MMM} – {Sun DD MMM})

### Work done
| Project | Summary | Days active |
|---------|---------|-------------|
| [[ProjectName]] | {what was done} | {N}/7 |

### Themes
- {cross-project theme}

### Goals progress
| Goal | Progress |
|------|----------|
| {goal} | on track / blocked / no activity |

### Stalled / needs attention
- {open item} — [[ProjectName]]

### Lessons captured this week
- {lesson} — [[ProjectName-lessons-learned]]
```

---

### 9. `search` — Cross-vault search

**When:** "search for X", "what do I know about X", "find X", "do I have notes on X",
"any lessons about X".

**Steps:**

1. **Extract search terms** from the query — strip filler words ("what do I know about",
   "find", "search for") to isolate the actual query.

2. **Scan these locations** (case-insensitive, whole-word preferred):
   - `projects/<n>/<n>.md` — purpose, stack, open items
   - `projects/<n>/<n>-lessons-learned.md` — accumulated lessons
   - `knowledge/topics/*.md` — concept pages
   - `knowledge/sources/*.md` — source summaries
   - `patterns/stack.md` and `patterns/decisions.md`

3. **Rank results:**
   - Exact phrase match > all keywords match > partial match
   - Lessons-learned and topic pages rank above context notes for conceptual queries

4. **Return grouped output** (omit empty groups):
```
## 🔍 Search: "{query}"

### Knowledge Topics
- [[knowledge/topics/topic]] — "{excerpt 1–2 lines}"

### Lessons Learned
- [[projects/ProjectName/ProjectName-lessons-learned]] — "{lesson text}"

### Projects
- [[projects/ProjectName/ProjectName]] — "{matching line from context note}"

### Patterns
- [[patterns/stack]] — "{excerpt}"
```

5. **If no matches:** "Nothing found for '{query}'. Consider running `ingest` if you have
   a source document on this topic."

6. **Do not log** search queries to CSV (too noisy). This command is read-only — no files written.

---

## Daily History

`history/YYYY-MM-DD.md` is a cross-project daily changelog — one file per day, one section per project touched. It is created on first write of the day and updated on every subsequent `log` or `sync` call.

**Format:**
```markdown
# YYYY-MM-DD

## [[projects/ProjectA/ProjectA|ProjectA]]
- {entry from ProjectA-history.md for this date}
- **Lessons:** {confirmed lesson 1}; {confirmed lesson 2}

## [[projects/ProjectB/ProjectB|ProjectB]]
- {entry from ProjectB-history.md for this date}
```

**Rules:**
- Create the file if it doesn't exist (from `history_daily_template.md`)
- If a section for this project already exists in today's file, append the new bullet points to it — do not create a duplicate section
- Use `[[projects/<n>/<n>|<n>]]` as the section heading — this is the graph edge connecting the daily file to each project node
- Keep entries concise: mirror what was written in `<n>-history.md`, no duplication of detail
- Only include a `**Lessons:**` line if there are confirmed lessons for that project on that day; omit if none

---

## Lessons Learned

`projects/<n>/<n>-lessons-learned.md` accumulates durable knowledge from sessions — bugs discovered, gotchas, architecture decisions, process insights — anything future-Claude shouldn't have to rediscover.

### When to run
During `sync` and `log`, after writing the history entry.

### Proposal flow (always interactive)

1. Review the conversation and the history entry just written
2. Identify candidates: process lessons, debugging findings, architecture decisions, gotchas — both categories count
3. Present candidates to the user:
   ```
   Proposed lessons learned:
   1. Don't retry on Garmin 429 — retrying worsens the ban; stop immediately and surface a wait message
   2. arnoldspumpclub.com is Shopify (/blogs/newsletter/<slug>), not Beehiiv — verify HTML structure before building scrapers
   3. Rolling date windows in tests instead of fixed past dates — avoids fixtures silently expiring

   Keep all? Skip any? Edit any? (e.g. "keep 1,3 / skip 2 / edit 1: ...")
   ```
4. Wait for confirmation. Do not write anything until the user responds.
5. If user says "skip" or "none", write nothing — do not create the file for this session.

### Writing

**`projects/<n>/<n>-lessons-learned.md`** — append-only, one dated block per session:
```markdown
# {ProjectName} — Lessons Learned

[[projects/{n}/{n}]]

## {ISO date}
- {confirmed lesson}
- {confirmed lesson}
```

- Create the file from `lessons_learned_template.md` if it doesn't exist
- If the file exists and already has an entry for today's date, append bullets to that block — do not create a duplicate date heading
- Keep lessons actionable and specific — not "be careful with dates" but "use `date.today() - timedelta(days=N)` in fixtures, never fixed past dates"

**`history/{ISO date}.md`** — add a `**Lessons:**` inline to the project section:
```markdown
- **Lessons:** {lesson 1}; {lesson 2}
```
- Semicolon-separated on one line; keep each lesson brief (10–15 words max)
- Only add if there are confirmed lessons; omit the line entirely if none

### Obsidian graph
Add `[[projects/<n>/<n>-lessons-learned]]` wikilink to `<n>.md` Links section (once, on first creation).

---

## Logging

Every action writes to **two** logs — one machine-readable, one human-readable.

### `logs/skill_runs.csv` — machine-readable (feeds `inspect`)

```
timestamp,project,command,success,error_notes
2025-03-21T14:30:00,GarminBot,context,true,
2025-03-21T14:35:00,cncSearch,sync,false,README.md not found
2025-03-21T15:00:00,_skill,inspect,true,amendment v2 accepted
```

Use `_skill` as project name for meta-actions (inspect, setup, init, lint).
Create header row if file doesn't exist. Never overwrite existing rows.

> **CSV safety:** Always wrap `error_notes` in double quotes. Escape any internal `"` as `""`. Example: `"README.md not found"`, `"token ""expired"" from API"`. This prevents CSV injection when the file is opened in spreadsheet applications.

### `logs/log.md` — human-readable (visible in Obsidian graph)

Append-only markdown file. One entry per action, with a consistent prefix tag for
parseability. Create with a `# Activity Log` header if it doesn't exist.

**Entry format:**
```markdown
## [{TAG}] {ISO date} — {ProjectName or _skill}: {one-line summary}
- {detail line 1}
- {detail line 2}
[[projects/{n}/{n}]]
```

**Tags:**
| Tag | Used for |
|-----|----------|
| `[INGEST]` | `sync` — project notes updated |
| `[KNOWLEDGE]` | `ingest` — knowledge source processed into wiki |
| `[QUERY]` | `context` — context loaded for a session |
| `[SESSION]` | `log` — session note recorded |
| `[LINT]` | `lint` — vault health check |
| `[AMEND]` | `inspect` — skill amendment proposed/applied |
| `[SETUP]` | `setup` / `init` — vault bootstrapped |

**Example entries:**
```markdown
## [INGEST] 2026-04-07 — GarminBot: sync after Garmin 429 fix
- Updated: README.md (stack), docker-compose.yml (new service)
- Lessons confirmed: 1
- Stale check: was 6 days overdue
[[projects/GarminBot/GarminBot]]

## [QUERY] 2026-04-07 — GarminBot: context loaded (debug intent)
- Branch: main | Last commit: abc1234 fix: stop retrying on 429
- Extra files loaded: lessons-learned (debug keywords detected)
[[projects/GarminBot/GarminBot]]

## [LINT] 2026-04-07 — _skill: vault health check
- Broken links: 0 | Orphan pages: 2 | Stale: cncSearch (14d)
- Missing CLAUDE.md: hetznercheck
- Auto-fixed: 1 CLAUDE.md created
[[logs/skill_runs]]

## [KNOWLEDGE] 2026-04-08 — _knowledge: ingested karpathy-llm-wiki
- Source: raw/article-karpathy.md | Format: markdown
- Topics created: agentic-workflows, context-management
- Proposals: 1 (improve-skill-ingest.md)
[[knowledge/index]]
```

Add `[[logs/log]]` wikilink to `system.md` (once, on first creation) so the log is
reachable from the graph root.

---

## Obsidian Graph Rules

Wikilinks are graph edges. Place them deliberately so the Obsidian graph view is meaningful.

| Link | Where to place it | Purpose |
|------|-------------------|---------|
| `[[projects/X/X]]` | system.md projects table | project node in graph |
| `[[projects/X/X\|X]]` | history/YYYY-MM-DD.md section headings | daily file → project edges |
| `[[projects/X/X-history]]` | X.md | connects project ↔ history |
| `[[projects/X/X-spec]]` | X.md Links section | connects project ↔ spec |
| `[[projects/X/X-lessons-learned]]` | X.md Links section | connects project ↔ lessons (added on first creation) |
| `[[patterns/stack]]` | X.md Links section | shared stack visible in graph |
| `[[patterns/decisions]]` | X.md or X-history.md | decision applies to project |
| `[[amendments/SKILL_vN_patch]]` | system.md or X-history.md | amendment visible from project |
| `[[ProjectName]]` | amendment files | which project triggered the fix |
| `[[logs/skill_runs]]` | amendment files | traceability to raw failure data |
| `[[logs/log]]` | system.md (once) | activity log reachable from graph root |
| `[[knowledge/index]]` | system.md (once) | knowledge wiki reachable from graph root |
| `[[knowledge/sources/X]]` | topic pages + project pages | source traceability |
| `[[knowledge/topics/X]]` | source pages + project pages | concept connections |
| `[[knowledge/proposals/X]]` | source pages | improvement proposal node |
| `[[me]]` | knowledge/index.md (once) | personal context visible in graph |

Never add duplicate wikilinks in the same file.

---

## Inline Amendment Suggestion (lightweight)

For minor issues that don't warrant a full inspect cycle, append at end of response:

```
---
⚠️ Suggestion: {scan of X found no readable files — consider adding Y to scan_targets}
Apply to config.yaml? (yes / skip)
```

Wait for confirmation before writing.

---

## Reference Files

Read only when needed:
- `references/obsidian_syntax.md` — wikilinks, tags, Dataview
- `references/project_fields.md` — valid field values for project notes
- `assets/templates/` — source templates (copy, never modify originals)

---

## Claude Code Hooks Integration

Claude Code hooks let the shell run commands automatically around tool calls and session events.
This section shows how to wire up the second brain so context loads and logs happen without
manual commands.

### Recommended hooks

Add these to `.claude/settings.json` (or `~/.claude/settings.json` for global config):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "cat \"$CLAUDE_PROJECT_DIR/CLAUDE.md\" 2>/dev/null | grep -q 'obsidian_vault:' && echo 'obsidian_vault found — say: load context'"
          }
        ]
      }
    ]
  }
}
```

**What this does:** When a Claude Code session starts in a project folder that has a `CLAUDE.md`
referencing the vault, it surfaces a reminder to run `load context`. This replaces the habit of
manually remembering to load context at session start.

### Manual `load context` trigger (simpler alternative)

If you prefer not to use hooks, add this to your project's `CLAUDE.md`:

```markdown
# Claude Code Context
obsidian_vault: ~/Documents/ObsidianVault
project: MyProject
Run: `load context` to initialise session memory.
```

The `Run:` line is visible to Claude at session start and acts as a soft prompt.
The `init` command creates this file automatically in every project folder.

### Hook for auto-logging (advanced)

To automatically propose a session log when you end a session:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Session ending — consider running: log session'"
          }
        ]
      }
    ]
  }
}
```

> **Note:** Hooks run shell commands, not Claude commands. The patterns above print reminders;
> Claude must still execute the skill commands. Full automation (hooks calling Claude) requires
> the Claude Code SDK — see the Claude Code documentation for agent-based approaches.

---

## Error Handling

| Situation | Action |
|-----------|--------|
| `config.yaml` missing | Run `setup` wizard — never proceed without it |
| `obsidian_vault_path` doesn't exist | Stop, show exact path, offer to create |
| Project not in vault | Offer to run `sync` to add it |
| Scan finds no readable files | Create stub `<n>.md`, log warning, suggest amendment |
| Duplicate `[[link]]` | Skip silently |
| Amendment conflicts with existing patch | Show both, ask user to choose |
| Git command fails (not a repo, no commits, git not in PATH) | Omit all git fields from Context Summary, continue normally; do not surface an error |
| `me.md` missing during ingest | Warn: "me.md not found — ingest will proceed without personal context. Run `setup second brain` to create it." Continue. |
| Source file format unreadable | Stop, tell user what format was detected and ask for a converted markdown version |
| `knowledge/index.md` missing | Create it from `knowledge_index_template.md` before proceeding |
| Proposal conflicts with existing proposal | Show both, ask user which to keep |

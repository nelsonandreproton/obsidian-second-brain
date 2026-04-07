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
    skill_runs.csv
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
12. Log to CSV

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
11. Log to CSV

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
prompt needed. Report both actions in a single summary response.

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
8. Update `history/{ISO date}.md` — append project section (see **Daily History** below)
9. Log to CSV

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

Every action appends one row to `{logs_folder}/skill_runs.csv`:

```
timestamp,project,command,success,error_notes
2025-03-21T14:30:00,GarminBot,context,true,
2025-03-21T14:35:00,cncSearch,sync,false,README.md not found
2025-03-21T15:00:00,_skill,inspect,true,amendment v2 accepted
```

Use `_skill` as project name for meta-actions (inspect, setup, init).
Create header row if file doesn't exist. Never overwrite existing rows.

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

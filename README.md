# obsidian-second-brain

A [Claude Code](https://claude.ai/claude-code) skill that maintains persistent project memory inside an Obsidian vault. Every session starts with full context — no re-explaining the stack, the decisions, or what was done last time.

The Obsidian graph view becomes a living knowledge graph: wikilinks between notes are the edges connecting projects, patterns, decisions, and daily history.

---

## How it works

Claude reads and writes structured Markdown notes to your Obsidian vault. On setup it scans your project folders, extracts purpose, stack, and services from README/Dockerfile/docker-compose, and creates three notes per project. From then on, loading context takes seconds.

### Vault structure

```
vault/
  config.yaml
  system.md                        ← master index: all projects + patterns
  projects/
    MyProject/
      MyProject.md                 ← stack, services, open items (loaded as context)
      MyProject-history.md         ← session changelog
      MyProject-spec.md            ← technical spec: APIs, env vars, data models (docs only)
  history/
    2026-03-21.md                  ← daily cross-project changelog
    2026-03-22.md
  patterns/
    stack.md                       ← shared tech conventions
    decisions.md                   ← architectural decisions + rationale
  amendments/                      ← proposed skill self-improvements
  templates/
  logs/
    skill_runs.csv                 ← audit trail
```

Each project folder uses the project name for all its files (`MyProject.md`, `MyProject-history.md`, `MyProject-spec.md`), so every node in the Obsidian graph is identifiable by name.

---

## Commands

| Say | What happens |
|-----|-------------|
| `setup second brain` | One-time wizard: vault path, project folders, writes config |
| `init` | Scans all project folders and creates notes; migrates old naming automatically |
| `load context` | Loads memory for the current project into the session |
| `sync project` | Re-scans a project after changes, updates notes |
| `add project X` | Adds a new project folder to the vault |
| `log session` | Appends what you did today to history and daily changelog |
| `inspect skill` | Analyses past failures, proposes self-improvements |

---

## Installation

This is a skill for [Claude Code](https://claude.ai/claude-code). To install it:

1. Copy the contents of this repo into your Claude Code skills folder:
   - **macOS/Linux:** `~/.claude/skills/obsidian-second-brain/`
   - **Windows:** `%APPDATA%\Claude\skills\obsidian-second-brain\`

2. Open Claude Code and say:

   ```
   setup second brain
   ```

3. Follow the wizard — it asks for your vault path and project folders, then runs `init` automatically.

---

## Requirements

- [Claude Code](https://claude.ai/claude-code)
- [Obsidian](https://obsidian.md) (free) — to view the knowledge graph
- An existing Obsidian vault, or an empty folder (the skill creates the structure)

---

## What gets created per project

Claude scans each project folder for `README.md`, `docker-compose.yml`, `Dockerfile`, `package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, or `Makefile` and creates three files:

### `MyProject.md` — context note
Loaded every session. Contains:
- **Purpose** — one or two sentences
- **Stack** — languages, frameworks, databases, infrastructure
- **Services & ports** — from docker-compose or Dockerfile
- **Open items** — TODOs noted during sessions

### `MyProject-history.md` — session changelog
Append-only log of what changed, when, and why. Last 3 entries are loaded with context.

### `MyProject-spec.md` — technical spec
Documentation only, never loaded as session context. Contains:
- Environment variables (full table with defaults)
- Data models and schema
- API endpoints
- Deployment instructions
- Key algorithms and non-obvious logic

---

## Daily history

Every `log` or `sync` also writes to `history/YYYY-MM-DD.md` — a cross-project daily changelog. Each section links back to the project node, so the Obsidian graph shows which projects were touched on any given day.

---

## Typical workflow

```
# Start of session
"load context"
→ Claude reads MyProject.md + last 3 history entries + patterns
→ Outputs a Context Summary and asks what you're working on

# Add a project that wasn't included at setup
"add project MyNewProject from C:/dev/MyNewProject"
→ Scans folder, creates 3 notes, adds to system.md

# After making changes
"sync project"
→ Re-scans files, shows diff, updates notes and daily changelog

# End of session
"log session"
→ Saves what was done to project history and today's daily file
→ Flags new patterns if any
```

---

## Self-improvement (inspect)

The skill logs every action to `logs/skill_runs.csv`. Running `inspect skill` analyses failures, identifies recurring patterns, and proposes amendments to its own `SKILL.md` — which you can accept, reject, or modify. Accepted amendments are versioned (`SKILL.v1.md`, `SKILL.v2.md`) so changes are traceable.

---

## Repository structure

```
SKILL.md                              ← skill definition loaded by Claude Code
assets/
  config_template.yaml               ← template for config.yaml
  templates/
    project_template.md
    spec_template.md
    history_template.md
    history_daily_template.md
    system_template.md
    amendment_template.md
references/
  obsidian_syntax.md                 ← wikilinks, tags, Dataview reference
  project_fields.md                  ← valid field values
```

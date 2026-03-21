# obsidian-second-brain

A [Claude Code](https://claude.ai/claude-code) skill that maintains persistent project memory inside an Obsidian vault. Every session starts with full context — no re-explaining the stack, the decisions, or what was done last time.

The Obsidian graph view becomes a living knowledge graph: wikilinks between notes are the edges connecting projects, patterns, and decisions.

---

## How it works

Claude reads and writes structured Markdown notes to your Obsidian vault. On setup it scans your project folders, extracts purpose, stack, and services from README/Dockerfile/docker-compose, and creates one note per project. From then on, loading context takes seconds.

### Vault structure

```
vault/
  config.yaml
  system.md                     ← master index: all projects + patterns
  projects/
    MyProject/
      project.md                ← stack, services, open items
      history.md                ← session changelog
  patterns/
    stack.md                    ← shared tech conventions
    decisions.md                ← architectural decisions + rationale
  amendments/                   ← proposed skill self-improvements
  templates/
  logs/
    skill_runs.csv              ← audit trail
```

---

## Commands

| Say | What happens |
|-----|-------------|
| `setup second brain` | One-time wizard: vault path, project folders, writes config |
| `init` | Scans all project folders and creates notes |
| `load context` | Loads memory for the current project into the session |
| `sync project` | Re-scans a project after changes, updates notes |
| `log session` | Appends what you did today to history.md |
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

Claude scans each project folder for `README.md`, `docker-compose.yml`, `Dockerfile`, `package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, or `Makefile` and extracts:

- **Purpose** — one or two sentences from the README
- **Stack** — languages, frameworks, databases, infrastructure
- **Services & ports** — from docker-compose or Dockerfile
- **Open items** — TODOs noted during sessions

---

## Typical workflow

```
# Start of session
"load context"
→ Claude reads project.md + last 3 history entries + patterns
→ Outputs a Context Summary and asks what you're working on

# After making changes
"sync project"
→ Re-scans files, shows diff, appends to history.md

# End of session
"log session"
→ Saves what was done, flags new patterns if any
```

---

## Self-improvement (inspect)

The skill logs every action to `logs/skill_runs.csv`. Running `inspect skill` analyses failures, identifies recurring patterns, and proposes amendments to its own `SKILL.md` — which you can accept, reject, or modify.

---

## Repository structure

```
SKILL.md                        ← skill definition loaded by Claude Code
assets/
  config_template.yaml          ← template for config.yaml
  templates/
    project_template.md
    history_template.md
    system_template.md
    amendment_template.md
references/
  obsidian_syntax.md            ← wikilinks, tags, Dataview reference
  project_fields.md             ← valid field values
```

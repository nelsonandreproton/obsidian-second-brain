# Obsidian Syntax Reference

Quick reference for Obsidian-specific Markdown used in this skill.

## Wikilinks

```markdown
[[NoteTitle]]                    # link to note by title
[[NoteTitle|Display Text]]       # link with custom label
[[folder/NoteTitle]]             # link to note in subfolder
```

Always use wikilinks for cross-references between vault notes.
Never use relative file paths like `./projects/GarminBot/project.md`.

## Tags

```markdown
#active         # inline tag
#needs-sync
#archived
```

Tags in Obsidian are searchable across the vault. Place them near the top of notes.

## Callouts (rendered in Obsidian)

```markdown
> [!NOTE]
> This is a note callout.

> [!WARNING]
> This is a warning.

> [!TIP]
> This is a tip.
```

Use callouts sparingly — only for genuinely important notices in project.md.

## Frontmatter (YAML)

Project notes include YAML frontmatter by default. This powers Dataview queries and Obsidian
search filters without requiring any extra plugins.

```yaml
---
type: project
status: active
stack: Python
last_sync: 2026-04-09
tags: [active, python, docker]
---
```

Valid `status` values: `active`, `archived`, `blocked`, `wip`, `stable`
Valid `type` values: `project`, `knowledge-topic`, `knowledge-source`, `personal-context`, `weekly-review`

## Dataview Queries (requires Dataview plugin)

These queries work out of the box once frontmatter is populated by the skill.

**All active projects, sorted by last sync:**
```dataview
TABLE stack, last_sync FROM "projects"
WHERE type = "project" AND status = "active"
SORT last_sync DESC
```

**Stale projects (not synced in 14+ days):**
```dataview
TABLE last_sync, stack FROM "projects"
WHERE type = "project" AND date(last_sync) < date(today) - dur(14 days)
SORT last_sync ASC
```

**All knowledge topics:**
```dataview
LIST FROM "knowledge/topics"
WHERE type = "knowledge-topic"
SORT file.name ASC
```

**Weekly reviews:**
```dataview
TABLE date_range FROM "weekly"
WHERE type = "weekly-review"
SORT week DESC
```

## Checkboxes

```markdown
- [ ] Open task
- [x] Completed task
- [/] In progress (Obsidian renders this)
```

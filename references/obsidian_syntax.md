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

## Dataview Queries (optional, if Dataview plugin installed)

```dataview
TABLE status, last_synced FROM "projects"
WHERE status = "Active"
SORT last_synced DESC
```

Don't generate Dataview blocks unless user confirms the plugin is installed.

## Frontmatter (YAML)

Obsidian supports YAML frontmatter for structured metadata:

```yaml
---
project: GarminBot
status: active
last_synced: 2025-03-21
tags: [active, docker, telegram]
---
```

The skill does **not** use frontmatter by default (keeps files human-readable).
Only add frontmatter if the user requests Dataview integration.

## Checkboxes

```markdown
- [ ] Open task
- [x] Completed task
- [/] In progress (Obsidian renders this)
```

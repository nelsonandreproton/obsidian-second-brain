# Project Fields Reference

All valid fields for `project.md` files and accepted values.

## Status Tags

| Tag | Meaning |
|-----|---------|
| `#active` | Being actively developed or maintained |
| `#archived` | No longer maintained, kept for reference |
| `#blocked` | Waiting on something external |
| `#needs-sync` | project.md is out of date, run `sync` |
| `#wip` | Work in progress, not yet stable |

## Status Field (table)

Plain text values: `Active`, `Archived`, `Blocked`, `WIP`, `Stable`

## Deployment Field

Examples: `Hetzner VPS`, `Docker Compose`, `HuggingFace Spaces`, `Render.com`,
`Oracle Cloud Free`, `Cloudflare Workers`, `Local only`

## Runtime Field

Examples: `Docker`, `Node.js 20`, `Python 3.11`, `Go 1.22`, `Bun`

## Infrastructure Field

Examples: `Hetzner CX22`, `Docker Compose`, `Nginx`, `Cloudflare Tunnel`,
`Traefik`, `Caddy`

## Open Items

Use standard GitHub-style checkboxes:
- `- [ ]` for open
- `- [x]` for done

Keep Open Items section to max 5 items. Move completed items to history.md.

## Links Section

Always include:
- `[[system]]` — backlink to system.md
- `[[patterns/stack]]` — if using shared stack

Optional:
- `[[patterns/decisions]]` — if an architectural decision applies
- External URLs (plain Markdown links, not Obsidian wikilinks)

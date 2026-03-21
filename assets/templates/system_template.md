# System Overview

> Central knowledge base for all projects. Last updated: {{last_updated}}

---

## Active Projects

| Project | Purpose | Stack | Status |
|---------|---------|-------|--------|
| [[GarminBot]] | Garmin activity + diet tracking | Python, Telegram | #active |
| [[cncSearch]] | Semantic church music search | Node.js, embeddings | #active |
| [[jmj2027]] | WYD 2027 news aggregator | {{stack}} | #active |
| [[hetznercheck]] | Hetzner server monitoring | {{stack}} | #active |
| [[homeserver]] | Entry point — updates all projects | Docker, Bash | #active |

---

## Infrastructure

- **Host:** Hetzner VPS
- **Orchestration:** Docker Compose
- **Notifications:** Telegram bots
- **Reverse proxy:** {{proxy}}
- **DNS / Tunnels:** {{tunnels}}

---

## Shared Patterns

- [[patterns/stack]] — recurring tech choices
- [[patterns/decisions]] — architecture decisions log

---

## Conventions

- All bots use Telegram for notifications
- Docker Compose per project, updated via [[homeserver]]
- Secrets in `.env` files, never committed
- {{custom_convention_1}}

---

## Recent Activity

| Date | Project | What happened |
|------|---------|---------------|
| {{date_1}} | [[{{project_1}}]] | {{summary_1}} |

---

## Quick Reference

```bash
# Update all projects
cd ~/homeserver && ./update.sh

# Check logs
docker compose logs -f --tail=50
```

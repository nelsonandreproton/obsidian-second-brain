---
type: project
status: {{status}}
stack: {{primary_stack}}
last_sync: {{sync_date}}
tags: [{{status_tag}}, {{stack_tag}}]
---

# {{ProjectName}}

> {{one_sentence_purpose}}

#{{status_tag}}

---

## Overview

| Field | Value |
|-------|-------|
| **Status** | {{status}} |
| **Last synced** | {{sync_date}} |
| **Location** | `{{project_path}}` |
| **Deployment** | {{deployment}} |

---

## Stack

- **Runtime:** {{runtime}}
- **Language:** {{language}}
- **Framework:** {{framework}}
- **Database:** {{database}}
- **Infrastructure:** {{infrastructure}}

---

## Services & Ports

| Service | Port | Notes |
|---------|------|-------|
| {{service_1}} | {{port_1}} | {{notes_1}} |

---

## Key Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | {{compose_purpose}} |
| `Dockerfile` | {{dockerfile_purpose}} |
| `README.md` | {{readme_purpose}} |

---

## Environment Variables

```
{{env_vars_example}}
```

---

## Dependencies

{{dependencies_list}}

---

## Links

- [[system]] — back to overview
- [[projects/{{ProjectName}}/{{ProjectName}}-history]]
- [[projects/{{ProjectName}}/{{ProjectName}}-spec]]
- [[patterns/stack]] — shared stack patterns
- {{external_link_1}}

---

## Open Items

- [ ] {{open_item_1}}

---

## Notes

{{free_notes}}

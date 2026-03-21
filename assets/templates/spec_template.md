---
name: {{name}}-spec
type: spec
last_updated: {{date}}
---

# {{name}} — Technical Spec

> Documentation only. Not loaded as session context.

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `VAR_NAME` | yes/no | description | — |

## Data Models

### `ModelName`
| Field | Type | Description |
|-------|------|-------------|
| `id` | int | primary key |

## API / Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | health check |

## Services & Ports

| Service | Port | Protocol | Notes |
|---------|------|----------|-------|
| — | — | — | — |

## Deployment

- **Platform:** {{platform}}
- **Deploy command:** `{{deploy_cmd}}`
- **Data volume:** `{{data_path}}`

## Key Algorithms / Logic

_Describe non-obvious logic, background jobs, scheduled tasks, retry strategies._

## Dependencies

_External APIs, third-party services, shared volumes with other projects._

## Links

- [[projects/{{name}}/{{name}}]]

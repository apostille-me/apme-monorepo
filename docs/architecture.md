# Architecture

Apostille Me uses a split-repo plus monorepo model:

- `apme-clients`: generated and hand-written SDKs.
- `apme-libs`: shared contracts and validation logic.
- `apme-infra`: Cloudflare Worker edge routes, bindings, and deployment config.
- `apostille-me.github.io`: Astro marketing site.
- `apme-monorepo`: integrated product development surface.

## Milestones

1. Wire monorepo packages to split `libs` contracts.
2. Generate OpenAPI from Worker route metadata.
3. Add e2e tests against Worker preview URLs and SDK clients.
4. Add observability propagation: request IDs, structured JSON logs, trace IDs, and dashboard links.

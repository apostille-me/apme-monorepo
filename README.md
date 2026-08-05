# apme-monorepo

High-context development surface for **Apostille Me**. Split repositories remain independently releasable; this monorepo provides a small, buildable control plane for local integration, contract validation, and repository-family orchestration.

## Layout

- `apps/control-plane` — Rust binary that validates and prints the service catalog
- `packages/catalog` — typed service metadata shared by tooling
- `apps/api`, `apps/web`, `apps/ops-console` — composition boundaries and integration notes
- `catalog.json` — machine-readable repository/service inventory
- `docs/architecture.md` — split-repo/monorepo ownership model

```bash
./scripts/test.sh
```

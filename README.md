# apme-monorepo

High-context development surface for **Apostille Me**. Split repositories remain independently releasable; this monorepo provides a small, buildable control plane for local integration, contract validation, and repository-family orchestration.

## Package composition

The root is a Zed package that composes clients, interfaces, shared libraries, sync, and shared authentication. It intentionally does **not** import `apme-infra` or `apme-cli`.

Runtime applications are pinned as Git submodules under `repos/`. Package-layer repositories remain Zed dependencies, enforcing a strict single-owner rule: a repository may be represented by Zed or by a gitlink, never both. See `docs/zed-and-submodules.md`.

## Layout

- `apps/control-plane` — Rust binary that validates and prints the service catalog
- `packages/catalog` — typed service metadata shared by tooling
- `repos/apme-api` — pinned API runtime submodule
- `repos/apme-web-leptos` — pinned Leptos web runtime submodule
- `repos/apme-web-dioxus` — pinned Dioxus web runtime submodule
- `repos/apme-web-mash` — pinned Maud/Axum/SeaORM/HTMX runtime submodule
- `apps/api`, `apps/web`, `apps/ops-console` — composition boundaries and integration notes
- `catalog.json` — machine-readable repository/service inventory
- `docs/architecture.md` — split-repo/monorepo ownership model
- `scripts/validate-zed-submodules.sh` — rejects dual ownership and CLI/infra imports
- `scripts/zed-install-with-submodules.sh` — guarded `zed install --git-submodules`

```bash
git submodule update --init --recursive
./scripts/test.sh
./scripts/validate-zed-submodules.sh
./scripts/zed-install-with-submodules.sh
```

# Repository and dependency composition

## Canonical short-name family

Use these repository and Zed package identities for all new work:

- `apme-interfaces`
- `apme-clients`
- `apme-libs`
- `apme-cli`
- `apme-sync`
- `apme-api`
- `apme-web-mash`
- `apme-web-leptos`
- `apme-web-dioxus`
- `apme-monorepo`
- planned: `apme-mcp-server.rs`

Do not introduce dependencies, releases, submodules, or documentation that make the full organization name a second package prefix.

## Redundant repositories

The following repositories are superseded by the short-name family:

| Superseded | Canonical |
| --- | --- |
| `apostille-me-clients` | `apme-clients` |
| `apostille-me-libs` | `apme-libs` |
| `apostille-me-infra` | `apme-infra` |
| `apostille-me-monorepo` | `apme-monorepo` |

Consolidation is deliberately conservative:

1. Freeze new feature and release work in the superseded repository.
2. Compare its commits and file inventory with the canonical repository.
3. Port only unique, useful behavior or documentation in a reviewed PR, preserving provenance in the PR body.
4. Redirect open work and package references to the canonical repository.
5. Archive the superseded repository only after its unique history has been accounted for.

A generic scaffold must not overwrite a more complete canonical implementation merely because filenames match.

## Zed packages and Git submodules

Reusable interfaces, clients, libraries, CLIs, generators, and tools are Zed dependencies declared in `.zpkg.toml` and locked reproducibly. Materialized package directories such as `.vendor/.zed` and `zed_modules` are never committed.

A retained gitlink is source composition, not package resolution. Every gitlink must be listed in `.zed-submodules.tsv` as a tab-separated path and exactly one classification:

```text
apps/example	workspace
references/compat	 experiment-reference
```

Valid classifications are `workspace`, `inventory`, `embedded-source`, `experiment-reference`, and `legacy`. Remove the extra space in the example before use; fields must be separated by one tab.

The same repository must not be both a Zed dependency and a gitlink in one composition. Infrastructure repositories remain separate and must not be added as monorepo submodules.

## Enforcement

`scripts/validate-composition.sh` rejects:

- long-name package identities;
- committed Zed materialization directories;
- unclassified gitlinks;
- a repository represented by both Zed and a submodule;
- infrastructure repositories used as submodules.

The regular test entrypoint runs this guard so local and CI behavior stay aligned.

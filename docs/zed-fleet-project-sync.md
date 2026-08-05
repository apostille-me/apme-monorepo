# Zed fleet and project synchronization

Status date: 2026-08-05

This document is the durable cross-system status record for the canonical `apostille-me` source fleet. It keeps GitHub repositories, GitHub Project #1, and the Linear project `github.com/apostille-me` aligned without creating a second package namespace.

## Canonical package graph

| Consumer | Required Zed dependencies |
| --- | --- |
| `apme-clients` | `apostille-me/apme-interfaces` |
| `apme-libs` | `apostille-me/apme-interfaces` |
| `apme-sync` | `apostille-me/apme-interfaces` |
| `apme-cli` | `apme-clients`, `apme-interfaces`, `apme-libs` |
| API and web servers | `apme-interfaces`, `apme-libs`, `apme-sync`, `shared-auth/shared-auth-clients` |
| `apme-monorepo` | clients, interfaces, libs, CLI, sync, and shared-auth clients |
| planned `apme-mcp-server.rs` | clients, interfaces, libs, CLI, sync, and shared-auth clients |
| planned `apme-e2e` | clients, interfaces, libs, and CLI |

Dependencies materialize under `.vendor/.zed`. Generated dependency trees are not committed or published. `.zpkg.lock` is generated only by a real successful resolver run; it is never fabricated from repository metadata.

## Completed delivery

- `apme-monorepo#5` completed the canonical short-name dependency graph.
- `apme-sync#1` added the missing Zed package identity and immutable interface dependency.
- `apme-libs#4` repaired the duplicate dependency table while preserving the interface contract.
- `apme-infra#2` retained infrastructure guidance without making infra a runtime package or application submodule.
- Long-name repositories are compatibility history only. New package coordinates, issues, pull requests, releases, and submodule adoption use `apme-*`.

## Remaining repositories

| Repository | GitHub tracker | Linear tracker |
| --- | --- | --- |
| `apostille-me/apme-mcp-server.rs` | `apme-monorepo#2` | `DEN-2285` |
| `apostille-me/apme-e2e` | `apme-monorepo#10` | `DEN-2286` |

Both repositories are blocked only on organization-level repository creation. Once created, the connected GitHub write path can create branches and files, push commits, open pull requests, inspect checks, and merge.

## Git and Zed ownership rule

Git submodules remain valid exact-source transport, but the same repository must not be represented twice in one composition. Intentional Zed adoption uses `zed overtake --git-submodules`: Git retains the committed gitlink and source checkout, while Zed owns package identity, dependency intent, materialization, and immutable lock provenance. Non-Zed submodules remain solely Git-managed.

Every committed gitlink must be classified in `.zed-submodules.tsv`. CI rejects unclassified gitlinks, long-name duplicate coordinates, committed `.vendor/.zed` or `zed_modules` content, and any repository used simultaneously as a Zed dependency and a submodule.

## Planning authorities

- GitHub organization: `apostille-me`
- GitHub Project: organization Project #1
- Linear project: `github.com/apostille-me`
- Parent fleet issue: `DEN-1951`
- Repository-creation capability issue: `DEN-319`

GitHub issues and implementation pull requests must link the matching Linear issue and organization Project. Status is updated in both systems when a repository is created, a PR is merged, or a dependency/lock gate changes.
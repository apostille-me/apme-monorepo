# Zed packages and Git submodules

`apme-monorepo` supports mixed checkouts without allowing two package managers to own the same repository.

## Ownership rule

- `.zpkg.toml` is authoritative for package dependencies and installs them under `.vendor/.zed`.
- `.gitmodules`, when present, may track composition-only repositories that are **not** listed in `[dependencies]`.
- Equivalent GitHub HTTPS, SSH, and `git://` URLs are normalized before comparison.
- `apme-infra` and `apme-cli` are intentionally excluded from both the Zed graph and Git submodules. Infrastructure is deployed independently; the CLI consumes the package graph rather than being composed by it.

## Commands

```bash
bash scripts/validate-zed-submodules.sh
bash scripts/zed-install-with-submodules.sh
```

The installer runs the ownership guard, delegates to `zed install --git-submodules`, and validates again. Generated `.vendor/.zed` state stays uncommitted. A `.zpkg.lock` should be committed only when produced by a real resolver run against published package versions.

For migration from legacy submodules, run `zed overtake --git-submodules` only in a clean worktree, review `.zpkg.toml` and `.zpkg.lock`, and re-run the validator before committing.

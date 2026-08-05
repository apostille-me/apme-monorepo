# Integration

Place pinned cross-repository compatibility tests here. Do not duplicate application or package source.

Each fixture must identify its source repository and exact revision. Reusable dependencies should resolve through canonical `apostille-me/apme-*` Zed coordinates; retained Git submodules must have an explicit composition role and must not duplicate a Zed dependency in the same workspace.

`zed overtake --git-submodules` imports each initialized submodule that declares its own `.zpkg.toml` into the root manifest and lockfile while retaining `.gitmodules` as a reversible transport mirror and recording exact gitlink commits and provenance.

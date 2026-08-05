# Integration

Place pinned cross-repository compatibility tests here. Do not duplicate application or package source.

Each fixture must identify its source repository and exact revision. Reusable dependencies should resolve through canonical `apostille-me/apme-*` Zed coordinates; retained Git submodules must have an explicit composition role and must not duplicate a Zed dependency in the same workspace.

Use root package manifests so `zed overtake --git-submodules` can adopt reviewed gitlinks while preserving `.gitmodules`, exact commits, and provenance.

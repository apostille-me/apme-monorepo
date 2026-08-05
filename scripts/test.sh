#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
node --test tests/*.test.mjs
node --check scripts/describe.mjs
node -e 'JSON.parse(require("node:fs").readFileSync("catalog.json", "utf8"));'
bash scripts/validate-composition.sh
if command -v cargo >/dev/null 2>&1; then
  cargo clippy --workspace --all-targets -- -D warnings
  cargo test --workspace --all-targets
  cargo run -q -p "apme-control-plane" >/dev/null
fi

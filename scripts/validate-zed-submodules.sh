#!/usr/bin/env bash
set -Eeuo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

[[ -f .zpkg.toml ]] || { echo 'missing .zpkg.toml' >&2; exit 1; }

dependencies="$({ awk '
  /^[[:space:]]*\[dependencies\][[:space:]]*$/ { in_deps=1; next }
  /^[[:space:]]*\[/ { in_deps=0 }
  in_deps {
    line=$0
    sub(/^[[:space:]]*"/, "", line)
    if (line != $0) { sub(/".*/, "", line); print tolower(line) }
  }
' .zpkg.toml; } | sort -u)"

if grep -Eq '(^|/)[^[:space:]]*(-infra|-cli)$' <<<"$dependencies"; then
  echo 'monorepo Zed dependencies must not import *-infra or *-cli' >&2
  grep -E '(^|/)[^[:space:]]*(-infra|-cli)$' <<<"$dependencies" >&2
  exit 1
fi

normalize_github_repo() {
  local value="${1%/}"
  value="${value%.git}"
  case "$value" in
    https://github.com/*) value="${value#https://github.com/}" ;;
    http://github.com/*) value="${value#http://github.com/}" ;;
    git://github.com/*) value="${value#git://github.com/}" ;;
    git@github.com:*) value="${value#git@github.com:}" ;;
    ssh://git@github.com/*) value="${value#ssh://git@github.com/}" ;;
    github.com/*) value="${value#github.com/}" ;;
    *) return 1 ;;
  esac
  [[ "$value" == */* && "$value" != */*/* ]] || return 1
  printf '%s\n' "${value,,}"
}

if [[ -f .gitmodules ]]; then
  while read -r key url; do
    [[ -n "${url:-}" ]] || continue
    identity="$(normalize_github_repo "$url" 2>/dev/null || true)"
    [[ -n "$identity" ]] || continue
    if grep -Fxq "$identity" <<<"$dependencies"; then
      printf '%s is represented both as a Zed dependency and a Git submodule (%s)\n' "$identity" "$key" >&2
      exit 1
    fi
    repo_name="${identity##*/}"
    if [[ "$repo_name" == *-infra || "$repo_name" == *-cli ]]; then
      printf 'monorepo must not import CLI/infra submodule: %s\n' "$identity" >&2
      exit 1
    fi
  done < <(git config -f .gitmodules --get-regexp '^submodule\..*\.url$' || true)

  git submodule sync --recursive
  git submodule status --recursive >/dev/null
fi

printf 'Zed/submodule ownership contract validated\n'

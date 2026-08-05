#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

product_org="apostille-me"
long_prefix="apostille-me"
allowed_classifications='^(workspace|inventory|embedded-source|experiment-reference|legacy)$'

manifests_file="$(mktemp)"
zed_deps_file="$(mktemp)"
gitlinks_file="$(mktemp)"
trap 'rm -f "$manifests_file" "$zed_deps_file" "$gitlinks_file"' EXIT

find . -type f -name '.zpkg.toml' -not -path './.git/*' -print | sort >"$manifests_file"

status=0
while IFS= read -r manifest; do
  [[ -n "$manifest" ]] || continue

  if grep -nE "\"${product_org}/${long_prefix}-(clients|interfaces|libs?|cli|sync|infra|monorepo|mcp-server\\.rs)\"" "$manifest"; then
    echo "error: $manifest references a superseded long-name package identity" >&2
    status=1
  fi

  sed -nE 's/^[[:space:]]*"([^"]+\/[^"]+)"[[:space:]]*=.*/\1/p' "$manifest" >>"$zed_deps_file"
done <"$manifests_file"
sort -u -o "$zed_deps_file" "$zed_deps_file"

if git ls-files | grep -Eq '(^|/)(\.vendor/\.zed|zed_modules)(/|$)'; then
  echo 'error: materialized Zed dependencies must not be committed' >&2
  status=1
fi

git ls-files --stage | awk '$1 == "160000" { print $4 }' >"$gitlinks_file"
if [[ -s "$gitlinks_file" ]]; then
  if [[ ! -f .zed-submodules.tsv ]]; then
    echo 'error: gitlinks exist but .zed-submodules.tsv is missing' >&2
    status=1
  else
    while IFS= read -r path; do
      classification="$(awk -F '\t' -v path="$path" '$1 == path { print $2; exit }' .zed-submodules.tsv)"
      if [[ ! "$classification" =~ $allowed_classifications ]]; then
        echo "error: gitlink '$path' lacks a valid classification" >&2
        status=1
      fi
    done <"$gitlinks_file"
  fi
fi

if [[ -f .gitmodules ]]; then
  if grep -nE '^[[:space:]]*url[[:space:]]*=.*[/@:][^[:space:]]*-infra(\.git)?[[:space:]]*$' .gitmodules; then
    echo 'error: infrastructure repositories must remain separate from app monorepos' >&2
    status=1
  fi

  while read -r key url; do
    [[ -n "${key:-}" && -n "${url:-}" ]] || continue
    name="${key#submodule.}"
    name="${name%.url}"
    path="$(git config -f .gitmodules --get "submodule.${name}.path")"

    repo="$url"
    case "$repo" in
      https://github.com/*) repo="${repo#https://github.com/}" ;;
      http://github.com/*) repo="${repo#http://github.com/}" ;;
      git@github.com:*) repo="${repo#git@github.com:}" ;;
      ssh://git@github.com/*) repo="${repo#ssh://git@github.com/}" ;;
      github:*) repo="${repo#github:}" ;;
      *) continue ;;
    esac
    repo="${repo%.git}"

    if grep -Fxq "$repo" "$zed_deps_file"; then
      echo "error: '$repo' is both a Zed dependency and gitlink at '$path'" >&2
      status=1
    fi
  done < <(git config -f .gitmodules --get-regexp '^submodule\..*\.url$' || true)
fi

if (( status != 0 )); then
  exit "$status"
fi

echo 'composition policy: ok'

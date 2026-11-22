#!/usr/bin/env bash
# Optional local publishing helper. Requires GitHub CLI authentication.
# Default visibility is private. Pass --public only when you intend public access.
set -euo pipefail

visibility="--private"
if [[ "${1:-}" == "--public" ]]; then
  visibility="--public"
elif [[ $# -gt 0 ]]; then
  printf '%s\n' 'Usage: bash scripts/publish_github.sh [--public]' >&2
  exit 2
fi

cd "$(dirname "$0")/.."
gh auth status
if git remote get-url origin >/dev/null 2>&1; then
  printf '%s\n' 'An origin remote already exists. Review it before publishing.' >&2
  exit 1
fi
if [[ -n "$(git status --porcelain)" ]]; then
  printf '%s\n' 'Commit and review local changes before publishing.' >&2
  exit 1
fi
owner="$(gh api user --jq .login)"
gh repo create "${owner}/mohit-analytics-portfolio" "$visibility" \
  --source . --remote origin --push \
  --description 'End-to-end Python and SQL portfolio: retail performance, customer retention and green logistics'
gh repo view --json url --jq .url

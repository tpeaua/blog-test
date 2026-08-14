#!/usr/bin/env bash
# Build the static site into dist/, then deploy.
#
# Usage:
#   scripts/deploy.sh                       build only (default)
#   DEPLOY_REMOTE=origin scripts/deploy.sh  build + push dist/ to gh-pages on $DEPLOY_REMOTE
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/build.py

if [[ -n "${DEPLOY_REMOTE:-}" ]]; then
  # Deploy dist/ as the gh-pages branch on the given remote.
  tmp="$(mktemp -d)"
  cp -R dist/. "$tmp/"
  git -C "$tmp" init -q
  git -C "$tmp" checkout -q -b gh-pages
  git -C "$tmp" add -A
  git -C "$tmp" -c user.email=deploy@local -c user.name=deploy commit -q -m "deploy: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  git -C "$tmp" push -q -f "$DEPLOY_REMOTE" gh-pages
  rm -rf "$tmp"
  echo "deployed dist/ -> $DEPLOY_REMOTE gh-pages"
else
  echo "built dist/ (set DEPLOY_REMOTE to push to GitHub Pages)"
fi

#!/usr/bin/env bash
# Add a new post: seed a team.Brief and run the agentic content team.
#
# Usage:
#   scripts/new-post.sh "Your topic" [slug] [tone]
set -euo pipefail
cd "$(dirname "$0")/.."

topic="${1:?usage: scripts/new-post.sh \"Topic\" [slug] [tone]}"
slug="${2:-$(printf '%s' "$topic" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-')}"
tone="${3:-conversational}"
date="$(date +%Y-%m-%d)"
provider="${PROVIDER:-pi}"

seed="$(mktemp)"
printf '{"team.Brief":{"topic":"%s","tone":"%s","slug":"%s","date":"%s"}}\n' \
  "$topic" "$tone" "$slug" "$date" > "$seed"

echo "Seeding team.Brief -> slug=$slug tone=$tone date=$date"
echo "Running the content team (writer -> editor -> reviewer -> gate -> publish -> build)..."
shift $(( $# < 3 ? $# : 3 ))  # consume topic/slug/tone; "$@" carries only extra meridian flags
meridian run .meridian/team/content-team.json \
  --allow llm,fs.write,bash.run \
  --provider "$provider" \
  --input "$seed" \
  --out ".meridian/team/run-$slug.jsonl" "$@"
rm -f "$seed"

echo
echo "Replay the run for \$0:  meridian replay .meridian/team/run-$slug.jsonl"

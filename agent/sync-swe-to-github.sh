#!/bin/bash
# sync-swe-to-github.sh
# Reads SWE*.md files and creates/updates GitHub Issues

set -euo pipefail

REPO="NinadAGokhale/local-ai-system"
PROJECT_NUMBER=1

for f in SWE*.md; do
  phase=$(echo "$f" | sed 's/\.md//' | tr '[:upper:]' '[:lower:]')
  title=$(head -1 "$f" | sed 's/^# //')
  body=$(cat "$f")

  echo "Creating issue: $title (phase:$phase)"

  gh issue create \
    --repo "$REPO" \
    --title "${phase}: ${title}" \
    --body "$body" \
    --label "phase:${phase}" \
    --project "$PROJECT_NUMBER" || echo "Failed to create issue for $f"
done

echo "Sync complete!"

#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
/usr/bin/python3 generate.py >> update.log 2>&1
/usr/bin/git add README.md public/data/repositories.json
if ! /usr/bin/git diff --cached --quiet; then
  /usr/bin/git commit -m "chore: refresh repository index $(date -u +%F)" >> update.log 2>&1
  /usr/bin/git push origin main >> update.log 2>&1
fi
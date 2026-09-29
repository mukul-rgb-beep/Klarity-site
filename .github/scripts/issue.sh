#!/usr/bin/env bash
# issue.sh open  "<exact title>" "<body>"    -> create the issue unless one with this exact title is open
# issue.sh close "<exact title>" "<comment>" -> close the open issue with this exact title, if any
set -euo pipefail
action=$1 title=$2 body=${3:-}
num=$(gh issue list --state open --limit 200 --json number,title \
      | jq -r --arg t "$title" '[.[] | select(.title == $t)][0].number // empty')
case $action in
  open)  [ -n "$num" ] || gh issue create --title "$title" --body "$body" --assignee mukul-rgb-beep ;;
  close) [ -z "$num" ] || gh issue close "$num" --comment "$body" ;;
  *) echo "usage: issue.sh open|close <title> <body>" >&2; exit 2 ;;
esac

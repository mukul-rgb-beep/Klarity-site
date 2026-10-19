#!/usr/bin/env python3
"""Post one message to X through the X API (v2, OAuth 1.0a user context).

  post_to_x.py "text and link"            -> prints the post's URL
  post_to_x.py "text and link" --dry-run  -> checks the keys are set and prints what it would send

Keys come from the environment: X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET
(the publish workflow passes them from the repo's Actions secrets).
Exit codes: 0 posted, 2 keys missing, 1 the API refused or could not be reached.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blogpub.xpost import oauth_header  # noqa: E402

ENDPOINT = "https://api.x.com/2/tweets"
KEYS = ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if len(args) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 1
    text = args[0]
    missing = [k for k in KEYS if not os.environ.get(k)]
    if missing:
        print("X keys are not set: " + ", ".join(missing), file=sys.stderr)
        return 2
    if "--dry-run" in sys.argv:
        print(f"would post ({len(text)} chars): {text}")
        return 0
    key, secret, token, token_secret = (os.environ[k] for k in KEYS)
    req = urllib.request.Request(ENDPOINT, data=json.dumps({"text": text}).encode(), method="POST", headers={
        "Authorization": oauth_header("POST", ENDPOINT, key, secret, token, token_secret),
        "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            post_id = json.load(r)["data"]["id"]
    except urllib.error.HTTPError as e:
        print(f"X API HTTP {e.code}: {e.read().decode(errors='replace')[:300]}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, KeyError, ValueError) as e:
        print(f"X API request failed: {e}", file=sys.stderr)
        return 1
    print(f"https://x.com/i/web/status/{post_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

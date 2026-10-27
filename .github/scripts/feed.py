#!/usr/bin/env python3
"""Rebuild blog/feed.xml from the blog index (publish.py also does this on every publish).

  feed.py           -> writes blog/feed.xml
  feed.py --check   -> exit 1 if blog/feed.xml is missing or stale
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from blogpub.feed import FEED, build_feed  # noqa: E402
from blogpub.tree import Tree  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    tree = Tree(ROOT)
    feed, path = build_feed(tree), ROOT / FEED
    if "--check" in sys.argv:
        if not path.exists() or path.read_text(encoding="utf-8") != feed:
            print(f"{FEED} is stale or missing: run .github/scripts/feed.py"); sys.exit(1)
        print(f"{FEED} up to date")
    else:
        path.write_text(feed, encoding="utf-8"); print(f"wrote {FEED}")

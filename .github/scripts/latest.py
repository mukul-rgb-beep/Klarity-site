#!/usr/bin/env python3
"""Rebuild the homepage's "Latest from the blog" row from the blog index (publish.py also does this on every publish).

  latest.py           -> rewrites the row in index.html
  latest.py --check   -> exit 1 if the row is stale or its markers are missing
"""
import pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from blogpub.home import HOME, latest_row, with_latest_row  # noqa: E402
from blogpub.tree import Tree  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    tree, path = Tree(ROOT), ROOT / HOME
    old = path.read_text(encoding="utf-8")
    new = with_latest_row(old, latest_row(tree))
    if new is None:
        print(f"{HOME} has no LATEST-POSTS markers (start and end, each exactly once)"); sys.exit(1)
    if "--check" in sys.argv:
        if new != old:
            print(f"the latest-posts row in {HOME} is stale: run .github/scripts/latest.py"); sys.exit(1)
        print(f"latest-posts row in {HOME} up to date")
    else:
        path.write_text(new, encoding="utf-8"); print(f"wrote the latest-posts row in {HOME}")

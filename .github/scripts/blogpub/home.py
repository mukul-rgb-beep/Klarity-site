"""The homepage's "Latest from the blog" row: the three newest posts, rebuilt on every publish.

The homepage is the page search engines fetch most often, so a link there is the quickest way
for a new post to be found. The row is built from the same Blog JSON-LD as the RSS feed.
"""
from __future__ import annotations

import html
import re

from blogpub import SITE
from blogpub.feed import _posts

HOME = "index.html"
START = "<!-- LATEST-POSTS: publish.py rewrites the cards between these two markers -->"
END = "<!-- /LATEST-POSTS -->"
COUNT = 3
DEFAULT_TAG = "Guide"
_CARD = re.compile(r'<article class="blog-card">.*?</article>', re.S)
_TAG = re.compile(r'<span class="tag">([^<]*)</span>')


def _tags(index: str) -> dict[str, str]:
    """Path of each post on the blog index -> the tag its card shows (Guide, Story, ...)."""
    tags = {}
    for card in _CARD.findall(index):
        href, tag = re.search(r'href="(/blog/[^"]+)"', card), _TAG.search(card)
        if href and tag:
            tags[href.group(1)] = tag.group(1).strip()
    return tags


def latest_row(tree) -> str:
    """The cards for the newest COUNT posts, one per line, as they sit between the markers."""
    index = tree.read("blog/index.html")
    tags = _tags(index)
    posts = sorted(_posts(index), key=lambda p: p.get("datePublished", ""), reverse=True)[:COUNT]
    lines = []
    for p in posts:
        path = p["url"].removeprefix(SITE)
        lines.append(f'      <a class="blog-card reveal" href="{html.escape(path)}">'
                     f'<span class="bc-tag">{html.escape(tags.get(path, DEFAULT_TAG), quote=False)}</span>'
                     f'<span class="bc-title">{html.escape(p.get("headline", ""), quote=False)}</span></a>\n')
    return "".join(lines)


def with_latest_row(home: str, row: str) -> str | None:
    """The homepage with `row` between the markers; None unless each marker is there exactly once, in order."""
    if home.count(START) != 1 or home.count(END) != 1:
        return None
    a, b = home.index(START), home.index(END)
    if b < a:
        return None
    line_end = home.find("\n", a)
    if line_end == -1 or line_end > b:
        return None
    line_start = home.rfind("\n", 0, b) + 1
    return home[:line_end + 1] + row + home[line_start:]

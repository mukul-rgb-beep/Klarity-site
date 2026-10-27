"""The blog's RSS feed (blog/feed.xml), built from the Blog JSON-LD in blog/index.html.

Search engines and feed readers re-fetch a feed often, so new posts are found quickly.
Each item's description is the post's meta description.
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone

from blogpub import SITE

FEED = "blog/feed.xml"
_LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
_DESC = re.compile(r'<meta name="description" content="([^"]*)"')


def _posts(index: str) -> list[dict]:
    for m in _LD.finditer(index):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if data.get("@type") == "Blog":
            return data.get("blogPost", [])
    return []


def _rfc822(day: str) -> str:
    # Posts go out at 09:00 IST, which is 03:30 UTC.
    d = datetime.strptime(day, "%Y-%m-%d").replace(hour=3, minute=30, tzinfo=timezone.utc)
    # Day and month names are fixed English, whatever the machine's locale.
    days, months = "Mon Tue Wed Thu Fri Sat Sun".split(), "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    return f"{days[d.weekday()]}, {d.day:02d} {months[d.month - 1]} {d.year} 03:30:00 +0000"


def build_feed(tree) -> str:
    posts = sorted(_posts(tree.read("blog/index.html")), key=lambda p: p.get("datePublished", ""), reverse=True)
    items = []
    for p in posts:
        url, date = p["url"], p.get("datePublished", "")
        page = f"blog/{url.rstrip('/').rsplit('/', 1)[1]}.html"
        desc = ""
        if tree.exists(page):
            m = _DESC.search(tree.read(page))
            desc = html.unescape(m.group(1)) if m else ""
        items.append(
            "    <item>\n"
            f"      <title>{html.escape(p.get('headline', ''), quote=False)}</title>\n"
            f"      <link>{url}</link>\n"
            f'      <guid isPermaLink="true">{url}</guid>\n'
            + (f"      <pubDate>{_rfc822(date)}</pubDate>\n" if date else "")
            + f"      <description>{html.escape(desc, quote=False)}</description>\n"
            "    </item>\n")
    latest = _rfc822(posts[0]["datePublished"]) if posts and posts[0].get("datePublished") else ""
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
            "  <channel>\n"
            "    <title>The Klarity Blog</title>\n"
            f"    <link>{SITE}/blog/</link>\n"
            f'    <atom:link href="{SITE}/{FEED}" rel="self" type="application/rss+xml"/>\n'
            "    <description>Plain-language guides to Mac storage: what is filling your disk and how to get space back.</description>\n"
            "    <language>en</language>\n"
            + (f"    <lastBuildDate>{latest}</lastBuildDate>\n" if latest else "")
            + "".join(items)
            + "  </channel>\n</rss>\n")

"""Scheduled publishing for klaritydisk.com blog posts."""

SITE = "https://www.klaritydisk.com"
SCHEDULED = "_scheduled"
TREEMAP = "blog/treemap-icicle-vs-sunburst.html"
MARKER = "<!-- SCHEDULED-CARDS: new cards are inserted below this line -->"


def url_for(file: str) -> str:
    """Public URL of a repo file: 'blog/x.html' -> SITE/blog/x, 'press.html' -> SITE/press."""
    if file == "index.html":
        return SITE + "/"
    if file.endswith("/index.html"):
        return f"{SITE}/{file[:-len('index.html')]}"
    return f"{SITE}/{file.removesuffix('.html')}"

"""Everything a publish changes, applied to a Tree overlay (nothing touches disk here)."""
from __future__ import annotations

import json
import re

from blogpub import MARKER, SITE, url_for

BLOGPOST_KEY = '"blogPost": ['


class ApplyError(Exception):
    pass


def _replace_once(text: str, find: str, replace: str, where: str) -> str:
    n = text.count(find)
    if n != 1:
        raise ApplyError(f"{where}: expected exactly 1 match, found {n}: {find[:60]!r}")
    return text.replace(find, replace, 1)


def _bump_lastmod(sitemap: str, url: str, day: str) -> str:
    pat = re.compile(r"(<loc>" + re.escape(url) + r"</loc><lastmod>)[^<]*(</lastmod>)")
    new, n = pat.subn(lambda m: m.group(1) + day + m.group(2), sitemap)
    if n != 1:
        raise ApplyError(f"sitemap.xml has {n} entries for {url}; expected 1")
    return new


def apply_package(tree, pkg, meta, day: str) -> list[str]:
    slug, url = pkg.slug, pkg.url
    bp = meta.schema("BlogPosting") or {}

    # 1. The page and its assets
    tree.write(f"blog/{slug}.html", tree.read(f"{pkg.path}/post.html"))
    for f in tree.files_under(f"{pkg.path}/assets"):
        target = "blog/" + f.rsplit("/", 1)[1]
        if tree.exists(target):
            raise ApplyError(f"asset {target} already exists")
        tree.write(target, tree.read_bytes(f))

    # 2. Blog index: card below the marker, BlogPosting first in the Blog JSON-LD
    index = tree.read("blog/index.html")
    if index.count(MARKER) != 1:
        raise ApplyError("blog/index.html must contain the SCHEDULED-CARDS marker exactly once")
    end = index.index("\n", index.index(MARKER)) + 1
    card = tree.read(f"{pkg.path}/card.html").rstrip("\n")
    index = index[:end] + card + "\n\n" + index[end:]
    if index.count(BLOGPOST_KEY) != 1:
        raise ApplyError('blog/index.html must contain "blogPost": [ exactly once')
    entry = json.dumps({"@type": "BlogPosting", "headline": bp.get("headline", meta.headline), "url": url,
                        "datePublished": pkg.publish_date,
                        "author": {"@type": "Person", "name": "Mukul Mehra"}})
    at = index.index(BLOGPOST_KEY) + len(BLOGPOST_KEY)
    sep = "" if index[at] == "]" else ", "
    tree.write("blog/index.html", index[:at] + entry + sep + index[at:])

    # 3. Sitemap: new line after /blog/, lastmod bumps
    sm = _bump_lastmod(tree.read("sitemap.xml"), SITE + "/blog/", day)
    blog_loc = f"<loc>{SITE}/blog/</loc>"
    line_end = sm.index("\n", sm.index(blog_loc)) + 1
    sm = (sm[:line_end] + f"  <url><loc>{url}</loc><lastmod>{day}</lastmod>"
          f"<changefreq>yearly</changefreq><priority>0.6</priority></url>\n" + sm[line_end:])
    inbound_urls: list[str] = []
    for link in pkg.inbound_links:
        u = url_for(link.file)
        if u not in inbound_urls:
            sm = _bump_lastmod(sm, u, day)
            inbound_urls.append(u)
    tree.write("sitemap.xml", sm)

    # 4. _redirects: .html -> clean URL, after the last /blog/ line
    lines = tree.read("_redirects").splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    blog_lines = [i for i, l in enumerate(lines) if l.startswith("/blog/")]
    at_line = (blog_lines[-1] + 1) if blog_lines else len(lines)
    lines.insert(at_line, f"/blog/{slug}.html /blog/{slug} 301\n")
    tree.write("_redirects", "".join(lines))

    # 5. Inbound links
    for link in pkg.inbound_links:
        if not tree.exists(link.file):
            raise ApplyError(f"inbound link target {link.file} does not exist")
        tree.write(link.file, _replace_once(tree.read(link.file), link.find, link.replace, link.file))

    # 6. The package itself goes (git history keeps it)
    for f in tree.files_under(pkg.path):
        tree.delete(f)
    return inbound_urls

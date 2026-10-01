#!/usr/bin/env python3
"""SEO skeleton of an HTML page, and a diff of two pages' skeletons.

  seo_snapshot.py OLD.html NEW.html   -> prints differences, exit 1 if any
Allowed to differ: JSON-LD softwareVersion / screenshot / image, og:image and twitter:image (cache-bust).
"""
import json, re, sys
from html.parser import HTMLParser

ALLOWED_LD = {"softwareVersion", "screenshot", "image"}
ALLOWED_META = {"og:image", "twitter:image", "og:image:width", "og:image:height"}


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.meta, self.links, self.canon = "", {}, set(), None
        self.h1, self.ld = [], []
        self._t = self._h1 = self._ld = False
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title": self._t = True
        elif tag == "meta" and (a.get("name") or a.get("property")):
            self.meta[a.get("name") or a.get("property")] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical": self.canon = a.get("href")
        elif tag == "a" and a.get("href", "").startswith(("/", "#", "https://www.klaritydisk.com")):
            self.links.add(a["href"].split("#")[0] or "#" + a["href"].split("#")[1])
        elif tag == "h1": self._h1, self._buf = True, []
        elif tag == "script" and a.get("type") == "application/ld+json": self._ld, self._buf = True, []

    def handle_endtag(self, tag):
        if tag == "title": self._t = False
        elif tag == "h1" and self._h1:
            self._h1 = False; self.h1.append(" ".join("".join(self._buf).split()))
        elif tag == "script" and self._ld:
            self._ld = False; self.ld.append(json.loads("".join(self._buf)))

    def handle_data(self, d):
        if self._t: self.title += d
        if self._h1 or self._ld: self._buf.append(d)


def snapshot(path):
    p = P(); p.feed(open(path, encoding="utf-8").read()); return p


def strip(d):
    if isinstance(d, dict): return {k: strip(v) for k, v in d.items() if k not in ALLOWED_LD}
    if isinstance(d, list): return [strip(x) for x in d]
    return d


def diff(old, new):
    o, n, out = snapshot(old), snapshot(new), []
    if o.title.strip() != n.title.strip(): out.append(f"title: {o.title!r} -> {n.title!r}")
    for k in sorted(set(o.meta) | set(n.meta)):
        if k not in ALLOWED_META and o.meta.get(k) != n.meta.get(k):
            out.append(f"meta {k}: {o.meta.get(k)!r} -> {n.meta.get(k)!r}")
    if o.canon != n.canon: out.append(f"canonical: {o.canon} -> {n.canon}")
    if o.h1 != n.h1: out.append(f"h1: {o.h1} -> {n.h1}")
    if strip(o.ld) != strip(n.ld): out.append("json-ld differs beyond allowed fields")
    missing = sorted(l for l in o.links - n.links if not l.startswith("#"))
    if missing: out.append(f"internal links dropped: {missing}")
    return out


if __name__ == "__main__":
    problems = diff(sys.argv[1], sys.argv[2])
    print("\n".join(problems) or "SEO skeleton identical (allowed fields aside)")
    sys.exit(1 if problems else 0)

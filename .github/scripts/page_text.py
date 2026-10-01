#!/usr/bin/env python3
"""Visible text (outside nav/header/footer/script/style) and element ids of a page.

  page_text.py OLD.html NEW.html  -> exit 1 and print the first difference if text or ids differ
"""
import re, sys
from html.parser import HTMLParser

SKIP = {"script", "style", "nav", "footer", "svg", "noscript"}


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth, self.words, self.ids = 0, [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"): self.ids.add(a["id"])
        if tag in SKIP or (tag == "header" and "nav" in (a.get("class") or "")): self.depth += 1

    def handle_endtag(self, tag):
        if (tag in SKIP or tag == "header") and self.depth: self.depth -= 1

    def handle_data(self, d):
        if not self.depth: self.words.extend(d.split())


def read(path):
    s = open(path, encoding="utf-8").read()
    body = s[s.find("<body"):] if "<body" in s else s
    p = P(); p.feed(body)
    return p


IGNORE_WORDS = {"🌙", "☀️", "Toggle", "theme"}
IGNORE_IDS = {"themeToggle", "mainNav", "navLinks", "navHamburger", "navBurger"}

if __name__ == "__main__":
    o, n = read(sys.argv[1]), read(sys.argv[2])
    ow = [w for w in o.words if w not in IGNORE_WORDS]
    nw = [w for w in n.words if w not in IGNORE_WORDS]
    if ow != nw:
        i = next((k for k, (a, b) in enumerate(zip(ow, nw)) if a != b), min(len(ow), len(nw)))
        print(f"text differs at word {i}: old {' '.join(ow[max(0,i-6):i+6])!r} | new {' '.join(nw[max(0,i-6):i+6])!r}")
        sys.exit(1)
    lost = sorted((o.ids - IGNORE_IDS) - n.ids)
    if lost:
        print(f"ids dropped: {lost}"); sys.exit(1)
    print("text and ids identical")

"""Read the metadata a blog post carries in its <head>, JSON-LD and FAQ block."""
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

TITLE_SUFFIX = " | Klarity Blog"
_FAQ = re.compile(r'<h3 class="faq-q">(.*?)</h3>\s*<p>(.*?)</p>', re.S)
_TITLE = re.compile(r"<title>.*?</title>", re.S)


def normalize(text: str) -> str:
    """Strip tags, decode entities, collapse whitespace."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", text)).split())


@dataclass
class PostMeta:
    title_tag: str = ""
    title: str = ""
    meta: dict[str, str] = field(default_factory=dict)
    canonical: str | None = None
    jsonld: list[dict] = field(default_factory=list)
    jsonld_errors: list[str] = field(default_factory=list)
    links: list[tuple[str, str]] = field(default_factory=list)
    faq_visible: list[tuple[str, str]] = field(default_factory=list)

    @property
    def headline(self) -> str:
        return self.title.removesuffix(TITLE_SUFFIX)

    def schema(self, type_: str) -> dict | None:
        return next((d for d in self.jsonld if isinstance(d, dict) and d.get("@type") == type_), None)

    @property
    def schema_url(self) -> str | None:
        bp = self.schema("BlogPosting") or {}
        m = bp.get("mainEntityOfPage", bp.get("url"))
        return m.get("@id") if isinstance(m, dict) else m


class _Parser(HTMLParser):
    def __init__(self, meta: PostMeta):
        super().__init__(convert_charrefs=True)
        self.m = meta
        self._in_title = False
        self._title: list[str] = []
        self._in_ld = False
        self._ld: list[str] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key and a.get("content") is not None:
                self.m.meta[key] = a["content"]
        elif tag == "link" and a.get("rel") == "canonical":
            self.m.canonical = a.get("href")
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld, self._ld = True, []
        elif tag == "a" and self._href is None:
            self._href, self._text = a.get("href") or "", []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            self.m.title = " ".join("".join(self._title).split())
        elif tag == "script" and self._in_ld:
            self._in_ld = False
            try:
                self.m.jsonld.append(json.loads("".join(self._ld)))
            except json.JSONDecodeError as e:
                self.m.jsonld_errors.append(str(e))
        elif tag == "a" and self._href is not None:
            self.m.links.append((self._href, " ".join("".join(self._text).split())))
            self._href = None

    def handle_data(self, data):
        if self._in_title:
            self._title.append(data)
        if self._in_ld:
            self._ld.append(data)
        if self._href is not None:
            self._text.append(data)


def parse_post(text: str) -> PostMeta:
    meta = PostMeta()
    t = _TITLE.search(text)
    meta.title_tag = t.group(0) if t else ""
    _Parser(meta).feed(text)
    meta.faq_visible = [(normalize(q), normalize(a)) for q, a in _FAQ.findall(text)]
    return meta

"""The site's SEO conventions (RESUME, 'SEO and marketing') as checks on a queued package."""
from __future__ import annotations

import re

from blogpub import MARKER, SITE, TREEMAP
from blogpub.apply import ApplyError, apply_package
from blogpub.post import parse_post

ANALYZER = "mac disk space analyzer"
GEO = re.compile(r"^https?://apps\.apple\.com/[a-z]{2}/")


def check_package(tree, pkg) -> list[str]:
    errs = list(pkg.errors)
    if not pkg.slug:
        return errs or ["slug is missing"]
    post_path, card_path = f"{pkg.path}/post.html", f"{pkg.path}/card.html"
    if not tree.exists(post_path):
        return errs + ["post.html is missing"]
    meta = parse_post(tree.read(post_path))
    url, href = pkg.url, f'href="/blog/{pkg.slug}"'
    bp = meta.schema("BlogPosting") or {}

    if tree.exists(f"blog/{pkg.slug}.html"):
        errs.append(f"blog/{pkg.slug}.html already exists")
    if f"/blog/{pkg.slug}.html " in tree.read("_redirects"):
        errs.append(f"_redirects already has /blog/{pkg.slug}.html")
    if f"<loc>{url}</loc>" in tree.read("sitemap.xml"):
        errs.append(f"sitemap.xml already lists {url}")

    if len(meta.headline) > 60:
        errs.append(f"title headline is {len(meta.headline)} characters; the limit is 60")

    found = {"meta description": meta.meta.get("description"),
             "og:description": meta.meta.get("og:description"),
             "twitter:description": meta.meta.get("twitter:description"),
             "BlogPosting description": bp.get("description")}
    missing = [k for k, v in found.items() if not v]
    if missing:
        errs.append("missing: " + ", ".join(missing))
    values = {v for v in found.values() if v}
    if len(values) > 1:
        errs.append("the four descriptions differ: " + "; ".join(f"{k}={v!r}" for k, v in found.items()))
    for v in values:
        if not 140 <= len(v) <= 155:
            errs.append(f"meta description is {len(v)} characters; it must be 140-155")

    for name, v in {"canonical": meta.canonical, "og:url": meta.meta.get("og:url"),
                    "BlogPosting URL": meta.schema_url}.items():
        if v != url:
            errs.append(f"{name} is {v!r}; expected {url}")
    for name, v in {"article:published_time": meta.meta.get("article:published_time"),
                    "BlogPosting datePublished": bp.get("datePublished")}.items():
        if v != pkg.publish_date:
            errs.append(f"{name} is {v!r}; expected {pkg.publish_date}")

    errs += [f"JSON-LD does not parse: {e}" for e in meta.jsonld_errors]
    for t in ("BlogPosting", "BreadcrumbList"):
        if not meta.schema(t):
            errs.append(f"{t} JSON-LD is missing")
    faq = meta.schema("FAQPage")
    if faq:
        pairs = [(" ".join(str(q.get("name", "")).split()),
                  " ".join(str((q.get("acceptedAnswer") or {}).get("text", "")).split()))
                 for q in faq.get("mainEntity", [])]
        if pairs != meta.faq_visible:
            diff = next(((a, b) for a, b in zip(pairs, meta.faq_visible) if a != b), None)
            errs.append(f"FAQPage JSON-LD does not match the visible FAQ "
                        f"({len(pairs)} vs {len(meta.faq_visible)} items; first difference: {diff})")
    elif meta.faq_visible:
        errs.append("the page has an FAQ block but no FAQPage JSON-LD")

    analyzer = [h for h, t in meta.links if t.casefold() == ANALYZER]
    if len(analyzer) != 1:
        errs.append(f"found {len(analyzer)} 'Mac disk space analyzer' links; there must be exactly 1")
    elif analyzer[0] not in ("/", SITE + "/"):
        errs.append(f"the 'Mac disk space analyzer' link points at {analyzer[0]!r}; it must point at /")
    for h, _ in meta.links:
        if GEO.match(h):
            errs.append(f"App Store link is not geo-neutral: {h}")

    links = pkg.inbound_links
    if len(links) < 4:
        errs.append(f"{len(links)} inbound links; at least 4 are needed")
    if not any(l.file == TREEMAP for l in links):
        errs.append(f"no inbound link from {TREEMAP}")
    for l in links:
        if not tree.exists(l.file):
            errs.append(f"inbound link target {l.file} does not exist")
            continue
        n = tree.read(l.file).count(l.find)
        if n != 1:
            errs.append(f"{l.file}: 'find' text matches {n} times; it must match exactly once: {l.find[:60]!r}")
        if href not in l.replace:
            errs.append(f"{l.file}: 'replace' has no {href}")

    if not tree.exists(card_path):
        errs.append("card.html is missing")
    elif href not in tree.read(card_path):
        errs.append(f"card.html has no {href}")
    if MARKER not in tree.read("blog/index.html"):
        errs.append("blog/index.html has no SCHEDULED-CARDS marker")
    for f in tree.files_under(f"{pkg.path}/assets"):
        name = f.rsplit("/", 1)[1]
        if tree.exists(f"blog/{name}"):
            errs.append(f"asset blog/{name} already exists")
    return errs


def check_all(tree, pkgs) -> dict[str, list[str]]:
    """Check each package, then apply them in date order on a scratch fork to catch clashes."""
    result: dict[str, list[str]] = {}
    scratch = tree.fork()
    for pkg in pkgs:
        errs = check_package(tree, pkg)
        if not errs:
            try:
                apply_package(scratch, pkg, parse_post(tree.read(f"{pkg.path}/post.html")), pkg.publish_date)
            except ApplyError as e:
                errs.append(f"clashes with an earlier package: {e}")
        result[pkg.dirname] = errs
    return result

"""Builders for a tiny fake Klarity-site used by every test."""
import html
import json
from pathlib import Path

SITE = "https://www.klaritydisk.com"
SLUG = "test-post"
DATE = "2026-10-06"
DIRNAME = f"{DATE}-{SLUG}"
HEADLINE = "Find Old Files You Forgot About on Your Mac"
DESC = ("It's a test description. " * 6).strip()          # 149 characters, has an apostrophe
FAQ = (("Is it safe to delete old files?", "Only once you've checked them. Klarity asks first."),)
CARD = ('        <!-- NEW POST: test post -->\n'
        '        <article class="blog-card"><a href="/blog/test-post">Test</a></article>\n')
LINKED = ("treemap-icicle-vs-sunburst", "a", "b", "c")

SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://www.klaritydisk.com/</loc><lastmod>2026-09-01</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>
  <url><loc>https://www.klaritydisk.com/press</loc><lastmod>2026-09-01</lastmod><changefreq>monthly</changefreq><priority>0.4</priority></url>
  <url><loc>https://www.klaritydisk.com/blog/</loc><lastmod>2026-09-01</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>
  <url><loc>https://www.klaritydisk.com/blog/a</loc><lastmod>2026-09-01</lastmod><changefreq>yearly</changefreq><priority>0.5</priority></url>
  <url><loc>https://www.klaritydisk.com/blog/b</loc><lastmod>2026-09-01</lastmod><changefreq>yearly</changefreq><priority>0.5</priority></url>
  <url><loc>https://www.klaritydisk.com/blog/c</loc><lastmod>2026-09-01</lastmod><changefreq>yearly</changefreq><priority>0.5</priority></url>
  <url><loc>https://www.klaritydisk.com/blog/treemap-icicle-vs-sunburst</loc><lastmod>2026-09-01</lastmod><changefreq>yearly</changefreq><priority>0.5</priority></url>
</urlset>
"""

REDIRECTS = """/index.html / 301
/blog/index.html /blog/ 301
/blog/a.html /blog/a 301
/blog/treemap-icicle-vs-sunburst.html /blog/treemap-icicle-vs-sunburst 301
/press.html /press 301
"""

BLOG_INDEX = """<html><head>
<script type="application/ld+json">{"@context": "https://schema.org", "@type": "Blog", "name": "The Klarity Blog", "blogPost": [{"@type": "BlogPosting", "headline": "A", "url": "https://www.klaritydisk.com/blog/a", "datePublished": "2026-09-01", "author": {"@type": "Person", "name": "Mukul Mehra"}}]}</script>
</head><body>
        <!-- SCHEDULED-CARDS: new cards are inserted below this line -->
        <!-- NEW POST: a -->
        <article class="blog-card"><a href="/blog/a">A</a></article>
</body></html>
"""


def _e(s):
    return html.escape(s, quote=True)


def make_post(slug=SLUG, date=DATE, headline=HEADLINE, desc=DESC, descs=None, canonical=None,
              og_url=None, schema_url=None, published_time=None, schema_date=None, faq=FAQ,
              schema_faq=None, body="", breadcrumb=True, analyzer_links=1,
              app_store="https://apps.apple.com/app/klarity-disk/id6758895498?mt=12"):
    url = f"{SITE}/blog/{slug}"
    d = {"meta": desc, "og": desc, "twitter": desc, "schema": desc} | (descs or {})
    blog = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": headline,
            "description": d["schema"], "author": {"@type": "Person", "name": "Mukul Mehra"},
            "datePublished": schema_date or date, "dateModified": schema_date or date,
            "mainEntityOfPage": schema_url or url}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": []}
    pairs = faq if schema_faq is None else schema_faq
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}
    lds = [blog] + ([crumbs] if breadcrumb else []) + ([faq_ld] if pairs else [])
    scripts = "\n".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in lds)
    faq_html = "\n".join(f'<h3 class="faq-q">{_e(q)}</h3>\n<p>{_e(a)}</p>' for q, a in faq)
    analyzer = " and ".join('<a href="https://www.klaritydisk.com/">Mac disk space analyzer</a>'
                            for _ in range(analyzer_links))
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<title>{_e(headline)} | Klarity Blog</title>
<meta name="description" content="{_e(d['meta'])}">
<link rel="canonical" href="{canonical or url}">
<meta property="og:description" content="{_e(d['og'])}">
<meta property="og:url" content="{og_url or url}">
<meta property="article:published_time" content="{published_time or date}">
<meta name="twitter:description" content="{_e(d['twitter'])}">
{scripts}
</head><body>
<p>Klarity, the {analyzer} I build.</p>
<p><a href="{app_store}">Klarity</a></p>
{body}
<h2>Questions people ask</h2>
{faq_html}
</body></html>
"""


def default_package(slug=SLUG, date=DATE):
    return {"slug": slug, "publish_date": date, "requires": None, "inbound_links": [
        {"file": f"blog/{name}.html", "find": f"Sentence in {name}.",
         "replace": f'Sentence in <a href="/blog/{slug}">{name}</a>.'} for name in LINKED]}


def make_package(root, dirname=DIRNAME, post=None, card=None, package=None, assets=None):
    root = Path(root)
    date, slug = dirname[:10], dirname[11:]
    pkg = root / "_scheduled" / dirname
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "post.html").write_text(post if post is not None else make_post(slug=slug, date=date))
    (pkg / "card.html").write_text(card if card is not None else CARD.replace("test-post", slug))
    (pkg / "package.json").write_text(json.dumps(package if package is not None
                                                  else default_package(slug, date), indent=2))
    for name, data in (assets or {}).items():
        (pkg / "assets").mkdir(exist_ok=True)
        (pkg / "assets" / name).write_bytes(data)
    return pkg


def make_site(root, with_package=True):
    root = Path(root)
    (root / "blog").mkdir(parents=True, exist_ok=True)
    (root / "sitemap.xml").write_text(SITEMAP)
    (root / "_redirects").write_text(REDIRECTS)
    (root / "blog" / "index.html").write_text(BLOG_INDEX)
    (root / "press.html").write_text("<html><body><p>Sentence in press.</p></body></html>\n")
    for name in LINKED:
        (root / "blog" / f"{name}.html").write_text(f"<html><body><p>Sentence in {name}.</p></body></html>\n")
    (root / "_scheduled").mkdir(exist_ok=True)
    (root / "_scheduled" / "README.md").write_text("Queued posts.\n")
    if with_package:
        make_package(root)
    return root

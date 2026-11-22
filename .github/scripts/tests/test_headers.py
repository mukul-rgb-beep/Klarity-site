"""The _headers file and the pages it protects (t22, 22 Nov 2026).

_headers sends a Content-Security-Policy on every address. A page that loads a script, image, font,
stylesheet, video or frame from a host the policy does not name would be broken by it, silently, for
every visitor. These tests read the policy from _headers and check every page in the site, the
queued posts in _scheduled/ included, so such a page fails here before it is pushed or published.
To add a third-party host, add it to the right directive in _headers first.
"""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
SITE = "https://www.klaritydisk.com"
REQUIRED = {
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "x-frame-options": "DENY",
}


def read_rules():
    rules, cur = [], None
    for line in (ROOT / "_headers").read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace():
            cur = (line.strip(), {})
            rules.append(cur)
        else:
            name, _, value = line.strip().partition(":")
            cur[1][name.strip().lower()] = value.strip()
    return rules


def policy():
    hs = dict(read_rules())["/*"]
    out = {}
    for part in hs["content-security-policy"].split(";"):
        words = part.split()
        if words:
            out[words[0]] = words[1:]
    return out


def allowed(url, directive, csp):
    sources = csp.get(directive, csp.get("default-src", []))
    if url.startswith("data:"):
        return "data:" in sources
    parts = urlsplit(url)
    if not parts.scheme and not parts.netloc:
        return "'self'" in sources  # relative: this site
    origin = f"{parts.scheme or 'https'}://{parts.netloc}"
    if origin == SITE:
        return "'self'" in sources
    return origin in sources


class Fetches(HTMLParser):
    """Collects (directive, url) for everything a page makes the browser fetch."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found = []
        self.in_style = False

    def add(self, directive, url):
        if url and not url.startswith(("#", "mailto:")):
            self.found.append((directive, url.strip()))

    def srcset(self, directive, value):
        for item in (value or "").split(","):
            if item.strip():
                self.add(directive, item.split()[0])

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and a.get("src"):
            self.add("script-src", a["src"])
        elif tag == "img":
            self.add("img-src", a.get("src"))
            self.srcset("img-src", a.get("srcset"))
        elif tag == "source":
            self.add("media-src" if a.get("type", "").startswith(("video", "audio")) else "img-src", a.get("src"))
            self.srcset("img-src", a.get("srcset"))
        elif tag in ("video", "audio"):
            self.add("media-src", a.get("src"))
            self.add("img-src", a.get("poster"))
        elif tag in ("iframe", "frame"):
            self.add("frame-src", a.get("src") or "about:blank")
        elif tag in ("object", "embed"):
            self.add("object-src", a.get("data") or a.get("src") or "plugin")
        elif tag == "form":
            self.add("form-action", a.get("action"))
        elif tag == "link":
            rel = (a.get("rel") or "").lower().split()
            if "stylesheet" in rel:
                self.add("style-src", a.get("href"))
            elif "icon" in rel or "apple-touch-icon" in rel or ("preload" in rel and a.get("as") == "image"):
                self.add("img-src", a.get("href"))
            elif "preload" in rel and a.get("as") == "font":
                self.add("font-src", a.get("href"))
            elif "preload" in rel and a.get("as") == "script":
                self.add("script-src", a.get("href"))
        elif tag == "style":
            self.in_style = True
        if a.get("style"):
            css_fetches(a["style"], self.add)

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            css_fetches(data, self.add)


def css_fetches(css, add):
    for m in re.finditer(r"@import\s+(?:url\()?\s*['\"]?([^'\")\s;]+)", css):
        add("style-src", m.group(1))
    for block in re.finditer(r"@font-face\s*{[^}]*}", css):
        for u in re.findall(r"url\(\s*['\"]?([^'\")]+)", block.group(0)):
            add("font-src", u)
    rest = re.sub(r"@font-face\s*{[^}]*}", "", css)
    for u in re.findall(r"url\(\s*['\"]?([^'\")]+)", rest):
        if not u.startswith("data:"):  # data: images are checked by the img-src test below
            add("img-src", u)


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if rel.parts[0] in (".git", ".github", "node_modules"):
            continue
        yield rel, p.read_text(encoding="utf-8")


class HeadersFileTest(unittest.TestCase):
    def test_every_address_gets_the_security_headers(self):
        hs = dict(read_rules()).get("/*")
        self.assertIsNotNone(hs, "_headers needs a /* rule")
        for name, value in REQUIRED.items():
            self.assertEqual(hs.get(name), value, name)
        self.assertIn("camera=()", hs.get("permissions-policy", ""))
        csp = policy()
        self.assertEqual(csp.get("frame-ancestors"), ["'none'"])
        self.assertEqual(csp.get("object-src"), ["'none'"])
        self.assertIn("'self'", csp.get("default-src", []))

    def test_no_hsts_from_the_file(self):
        # HSTS is set in the Cloudflare dashboard; a second one from here could disagree with it.
        for _, hs in read_rules():
            self.assertNotIn("strict-transport-security", hs)

    def test_cloudflare_limits(self):
        text = (ROOT / "_headers").read_text()
        self.assertLessEqual(len(read_rules()), 100)
        for line in text.splitlines():
            self.assertLessEqual(len(line), 2000)

    def test_the_share_bar_keeps_clipboard_and_share_sheet(self):
        pp = dict(read_rules())["/*"].get("permissions-policy", "")
        self.assertNotIn("clipboard-write", pp)
        self.assertNotIn("web-share", pp)

    def test_cloudflare_web_analytics_is_allowed(self):
        csp = policy()
        self.assertIn("https://static.cloudflareinsights.com", csp["script-src"])
        self.assertIn("'self'", csp["connect-src"])  # /cdn-cgi/rum and the bot check
        # Inline scripts and onclick handlers are on most pages and are rewritten by the publisher.
        self.assertIn("'unsafe-inline'", csp["script-src"])
        self.assertIn("'unsafe-inline'", csp["style-src"])


class PagesFitThePolicyTest(unittest.TestCase):
    def test_every_page_loads_only_what_the_policy_allows(self):
        csp = policy()
        problems = []
        for rel, html in pages():
            parser = Fetches()
            parser.feed(html)
            for directive, url in parser.found:
                if url == "about:blank" and directive == "frame-src":
                    problems.append(f"{rel}: an <iframe> (frame-src)")
                elif url == "plugin":
                    problems.append(f"{rel}: an <object>/<embed> (object-src 'none')")
                elif not allowed(url, directive, csp):
                    problems.append(f"{rel}: {url} ({directive})")
        self.assertEqual(problems, [], "Pages load something the Content-Security-Policy in _headers blocks. "
                         "Add the host to _headers first, or host the file on the site.")

    def test_site_css_loads_only_what_the_policy_allows(self):
        csp = policy()
        problems = []
        for css in sorted(ROOT.glob("css/*.css")):
            found = []
            css_fetches(css.read_text(encoding="utf-8"), lambda d, u: found.append((d, u)))
            problems += [f"{css.name}: {u} ({d})" for d, u in found if not allowed(u, d, csp)]
        self.assertEqual(problems, [])

    def test_data_images_need_img_src_data(self):
        uses_data = any("url(\"data:" in c.read_text() or "url('data:" in c.read_text() or "url(data:" in c.read_text()
                        for c in ROOT.glob("css/*.css"))
        if uses_data:
            self.assertIn("data:", policy()["img-src"])

    def test_the_checker_catches_a_blocked_embed(self):
        # Guards the guard: a YouTube embed and an outside image must be reported.
        csp = policy()
        parser = Fetches()
        parser.feed('<iframe src="https://www.youtube.com/embed/x"></iframe><img src="https://i.ytimg.com/a.jpg">'
                    '<a href="https://www.youtube.com/watch?v=x">a link is fine</a><img src="/img/ok.webp">')
        blocked = [u for d, u in parser.found if not allowed(u, d, csp)]
        self.assertEqual(blocked, ["https://www.youtube.com/embed/x", "https://i.ytimg.com/a.jpg"])


if __name__ == "__main__":
    unittest.main()

import json
import re
import tempfile
import unittest
from pathlib import Path

from blogpub import MARKER
from blogpub.apply import ApplyError, apply_package
from blogpub.package import load_packages
from blogpub.post import parse_post
from blogpub.tree import Tree
from tests.helpers import DIRNAME, make_package, make_post, make_site


class ApplyTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_site(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def run_apply(self, day="2026-10-06"):
        tree = Tree(self.root)
        [pkg] = load_packages(tree)
        urls = apply_package(tree, pkg, parse_post(tree.read(f"{pkg.path}/post.html")), day)
        return tree, urls

    def test_full_publish(self):
        tree, urls = self.run_apply()
        self.assertTrue(tree.exists("blog/test-post.html"))
        index = tree.read("blog/index.html")
        self.assertIn(MARKER + "\n        <!-- NEW POST: test post -->", index)
        self.assertLess(index.index("/blog/test-post"), index.index("<!-- NEW POST: a -->"))
        ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', index).group(1))
        self.assertEqual(ld["blogPost"][0], {"@type": "BlogPosting",
                         "headline": "Find Old Files You Forgot About on Your Mac",
                         "url": "https://www.klaritydisk.com/blog/test-post", "datePublished": "2026-10-06",
                         "author": {"@type": "Person", "name": "Mukul Mehra"}})
        self.assertEqual(len(ld["blogPost"]), 2)
        sm = tree.read("sitemap.xml").splitlines()
        blog_i = next(i for i, l in enumerate(sm) if "<loc>https://www.klaritydisk.com/blog/</loc>" in l)
        self.assertIn("<lastmod>2026-10-06</lastmod>", sm[blog_i])
        self.assertEqual(sm[blog_i + 1], "  <url><loc>https://www.klaritydisk.com/blog/test-post</loc>"
                         "<lastmod>2026-10-06</lastmod><changefreq>yearly</changefreq><priority>0.6</priority></url>")
        for name in ("a", "b", "c", "treemap-icicle-vs-sunburst"):
            line = next(l for l in sm if f"/blog/{name}</loc>" in l)
            self.assertIn("<lastmod>2026-10-06</lastmod>", line)
            self.assertIn(f'<a href="/blog/test-post">{name}</a>', tree.read(f"blog/{name}.html"))
        self.assertIn("<lastmod>2026-09-01</lastmod>", next(l for l in sm if "/press</loc>" in l))
        red = tree.read("_redirects").splitlines()
        self.assertEqual(red[red.index("/blog/treemap-icicle-vs-sunburst.html /blog/treemap-icicle-vs-sunburst 301") + 1],
                         "/blog/test-post.html /blog/test-post 301")
        self.assertEqual(tree.files_under(f"_scheduled/{DIRNAME}"), [])
        self.assertEqual(sorted(urls), sorted(f"https://www.klaritydisk.com/blog/{n}"
                                              for n in ("a", "b", "c", "treemap-icicle-vs-sunburst")))

    def test_late_publish_uses_run_date_for_lastmod(self):
        tree, _ = self.run_apply(day="2026-10-09")
        self.assertIn("<loc>https://www.klaritydisk.com/blog/test-post</loc><lastmod>2026-10-09</lastmod>",
                      tree.read("sitemap.xml"))

    def test_unicode_headline_is_escaped_like_existing_entries(self):
        make_package(self.root, DIRNAME, post=make_post(headline="Don\u2019t Panic \u2014 Mac Files"))
        tree, _ = self.run_apply()
        index = tree.read("blog/index.html")
        self.assertIn('"headline": "Don\\u2019t Panic \\u2014 Mac Files"', index)
        json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', index).group(1))

    def test_redirects_without_trailing_newline(self):
        (self.root / "_redirects").write_text("/blog/a.html /blog/a 301")
        tree, _ = self.run_apply()
        self.assertEqual(tree.read("_redirects"), "/blog/a.html /blog/a 301\n/blog/test-post.html /blog/test-post 301\n")

    def test_assets_are_copied(self):
        make_package(self.root, DIRNAME, assets={"shot.png": b"\x89PNG"})
        tree, _ = self.run_apply()
        self.assertEqual(tree.read_bytes("blog/shot.png"), b"\x89PNG")

    def test_find_mismatch_raises(self):
        (self.root / "blog" / "a.html").write_text("<p>changed</p>")
        with self.assertRaises(ApplyError):
            self.run_apply()

    def test_unknown_sitemap_url_raises(self):
        (self.root / "sitemap.xml").write_text((self.root / "sitemap.xml").read_text().replace("/blog/c<", "/blog/zz<"))
        with self.assertRaises(ApplyError):
            self.run_apply()


if __name__ == "__main__":
    unittest.main()

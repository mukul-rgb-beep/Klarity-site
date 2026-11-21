import json
import tempfile
import unittest
from pathlib import Path

from blogpub.apply import ApplyError, apply_package
from blogpub.checks import check_all
from blogpub.home import END, HOME, START, latest_row, with_latest_row
from blogpub.package import load_packages
from blogpub.post import parse_post
from blogpub.tree import Tree
from tests.helpers import HEADLINE, make_site

CARD = '      <a class="blog-card reveal" href="/blog/{slug}"><span class="bc-tag">{tag}</span><span class="bc-title">{title}</span></a>\n'


def blog_index(posts):
    """A blog index holding `posts` as (slug, date, headline, tag or None)."""
    ld = {"@context": "https://schema.org", "@type": "Blog", "blogPost": [
        {"@type": "BlogPosting", "headline": h, "url": f"https://www.klaritydisk.com/blog/{s}", "datePublished": d}
        for s, d, h, _ in posts]}
    cards = "".join(f'<article class="blog-card">\n<div class="blog-meta"><span class="tag">{t}</span></div>\n'
                    f'<h2><a href="/blog/{s}">{h}</a></h2>\n</article>\n' for s, _, h, t in posts if t)
    return (f'<html><head>\n<script type="application/ld+json">{json.dumps(ld)}</script>\n</head><body>\n'
            f'        <!-- SCHEDULED-CARDS: new cards are inserted below this line -->\n{cards}</body></html>\n')


class HomeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_site(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def publish(self, day="2026-10-06"):
        tree = Tree(self.root)
        [pkg] = load_packages(tree)
        return tree, apply_package(tree, pkg, parse_post(tree.read(f"{pkg.path}/post.html")), day)

    def test_row_is_the_three_newest_posts_newest_first(self):
        (self.root / "blog" / "index.html").write_text(blog_index([
            ("old", "2026-08-01", "Old", "Guide"), ("new", "2026-10-03", "New & <Shiny>", "Story"),
            ("mid", "2026-09-15", "Mid", "Guide"), ("older", "2026-07-01", "Older", "Guide")]))
        self.assertEqual(latest_row(Tree(self.root)),
                         CARD.format(slug="new", tag="Story", title="New &amp; &lt;Shiny&gt;")
                         + CARD.format(slug="mid", tag="Guide", title="Mid")
                         + CARD.format(slug="old", tag="Guide", title="Old"))

    def test_post_without_a_card_tag_is_a_guide(self):
        (self.root / "blog" / "index.html").write_text(blog_index([("solo", "2026-10-03", "Solo", None)]))
        self.assertEqual(latest_row(Tree(self.root)), CARD.format(slug="solo", tag="Guide", title="Solo"))

    def test_only_the_lines_between_the_markers_change(self):
        home = f"<p>above</p>\n    {START}\n      <a>stale</a>\n    {END}\n<p>below</p>\n"
        self.assertEqual(with_latest_row(home, "      <a>fresh</a>\n"),
                         f"<p>above</p>\n    {START}\n      <a>fresh</a>\n    {END}\n<p>below</p>\n")
        self.assertEqual(with_latest_row(with_latest_row(home, ""), "      <a>fresh</a>\n"),
                         with_latest_row(home, "      <a>fresh</a>\n"))

    def test_missing_doubled_or_swapped_markers_are_refused(self):
        for home in ("<p>none</p>\n", f"{START}\n", f"{END}\n", f"{START}\n{START}\n{END}\n",
                     f"{END}\n{START}\n", f"{START} {END}\n"):
            self.assertIsNone(with_latest_row(home, "x\n"), home)

    def test_publish_puts_the_new_post_first_on_the_homepage(self):
        tree, urls = self.publish()
        home = tree.read(HOME)
        self.assertIn(START + "\n" + CARD.format(slug="test-post", tag="Guide", title=HEADLINE)
                      + CARD.format(slug="a", tag="Guide", title="A") + "      " + END, home)
        self.assertIn("https://www.klaritydisk.com/", urls)
        line = next(l for l in tree.read("sitemap.xml").splitlines() if "<loc>https://www.klaritydisk.com/</loc>" in l)
        self.assertIn("<lastmod>2026-10-06</lastmod>", line)

    def test_publish_fails_without_the_markers(self):
        (self.root / "index.html").write_text("<html><body>no row</body></html>\n")
        with self.assertRaises(ApplyError) as cm:
            self.publish()
        self.assertIn("LATEST-POSTS", str(cm.exception))

    def test_check_reports_missing_markers(self):
        (self.root / "index.html").write_text("<html><body>no row</body></html>\n")
        tree = Tree(self.root)
        [errs] = check_all(tree, load_packages(tree)).values()
        self.assertTrue(any("LATEST-POSTS" in e for e in errs), errs)

    def test_check_passes_with_the_markers(self):
        tree = Tree(self.root)
        self.assertEqual(list(check_all(tree, load_packages(tree)).values()), [[]])


if __name__ == "__main__":
    unittest.main()

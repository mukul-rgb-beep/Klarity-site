import json
import tempfile
import unittest
from pathlib import Path

from blogpub.checks import check_all, check_package
from blogpub.package import load_packages
from blogpub.tree import Tree
from tests.helpers import DESC, DIRNAME, default_package, make_package, make_post, make_site


class ChecksTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_site(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def errors(self, **post_kw):
        if post_kw:
            make_package(self.root, DIRNAME, post=make_post(**post_kw))
        tree = Tree(self.root)
        return check_package(tree, load_packages(tree)[0])

    def assertError(self, fragment, errs):
        self.assertTrue(any(fragment in e for e in errs), f"{fragment!r} not in {errs}")

    def set_package(self, data):
        (self.root / "_scheduled" / DIRNAME / "package.json").write_text(json.dumps(data))

    def test_valid_package_passes(self):
        self.assertEqual(self.errors(), [])

    def test_title_too_long(self):
        self.assertError("limit is 60", self.errors(headline="X" * 61))

    def test_description_length(self):
        self.assertError("must be 140-155", self.errors(desc="Too short."))

    def test_descriptions_differ(self):
        self.assertError("differ", self.errors(descs={"og": DESC.replace("test", "tost")}))

    def test_wrong_canonical(self):
        self.assertError("canonical", self.errors(canonical="https://klaritydisk.com/blog/test-post"))

    def test_schema_date_mismatch(self):
        self.assertError("datePublished", self.errors(schema_date="2026-10-05"))

    def test_missing_breadcrumb(self):
        self.assertError("BreadcrumbList", self.errors(breadcrumb=False))

    def test_faq_mismatch(self):
        self.assertError("FAQPage", self.errors(schema_faq=(("Is it safe to delete old files?", "Different."),)))

    def test_analyzer_anchor_count(self):
        self.assertError("exactly 1", self.errors(analyzer_links=0))
        self.assertError("exactly 1", self.errors(analyzer_links=2))

    def test_geo_app_store_link(self):
        self.assertError("geo-neutral", self.errors(app_store="https://apps.apple.com/in/app/klarity-disk/id6758895498"))

    def test_too_few_links_and_no_treemap(self):
        data = default_package()
        data["inbound_links"] = data["inbound_links"][1:]
        self.set_package(data)
        errs = self.errors()
        self.assertError("at least 4", errs)
        self.assertError("treemap-icicle-vs-sunburst", errs)

    def test_find_must_match_once(self):
        (self.root / "blog" / "a.html").write_text("<p>Sentence in a.</p><p>Sentence in a.</p>")
        self.assertError("matches 2 times", self.errors())

    def test_replace_needs_link(self):
        data = default_package()
        data["inbound_links"][0]["replace"] = "no link"
        self.set_package(data)
        self.assertError("'replace' has no", self.errors())

    def test_card_needs_link(self):
        make_package(self.root, DIRNAME, card="<article>nothing</article>\n")
        self.assertError("card.html", self.errors())

    def test_slug_already_live(self):
        (self.root / "blog" / "test-post.html").write_text("live")
        self.assertError("already exists", self.errors())

    def test_marker_missing(self):
        p = self.root / "blog" / "index.html"
        p.write_text(p.read_text().replace("SCHEDULED-CARDS", "X"))
        self.assertError("marker", self.errors())

    def test_asset_collision(self):
        make_package(self.root, DIRNAME, assets={"a.html": b"x"})
        self.assertError("asset blog/a.html", self.errors())

    def test_check_all_finds_clash_between_packages(self):
        # A second package whose find text the first one rewrites
        second = default_package("second", "2026-10-13")
        second["inbound_links"][0]["find"] = "Sentence in treemap-icicle-vs-sunburst."
        make_package(self.root, "2026-10-13-second", package=second)
        tree = Tree(self.root)
        result = check_all(tree, load_packages(tree))
        self.assertEqual(result[DIRNAME], [])
        self.assertError("clashes", result["2026-10-13-second"])

    def test_check_all_rejects_two_packages_with_one_slug(self):
        make_package(self.root, "2026-10-07-test-post", package=default_package("test-post", "2026-10-07"))
        tree = Tree(self.root)
        result = check_all(tree, load_packages(tree))
        self.assertError("blog/test-post.html already exists", result["2026-10-07-test-post"])


if __name__ == "__main__":
    unittest.main()

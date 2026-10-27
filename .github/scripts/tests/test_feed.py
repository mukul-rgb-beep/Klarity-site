import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from blogpub.apply import apply_package
from blogpub.feed import FEED, build_feed
from blogpub.package import load_packages
from blogpub.post import parse_post
from blogpub.tree import Tree
from tests.helpers import DESC, HEADLINE, make_site


class FeedTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_site(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_feed_lists_every_post(self):
        rss = ET.fromstring(build_feed(Tree(self.root)))
        items = rss.findall("channel/item")
        self.assertEqual([i.findtext("link") for i in items], ["https://www.klaritydisk.com/blog/a"])
        self.assertEqual(items[0].findtext("pubDate"), "Tue, 01 Sep 2026 03:30:00 +0000")

    def test_publish_puts_new_post_first(self):
        tree = Tree(self.root)
        [pkg] = load_packages(tree)
        apply_package(tree, pkg, parse_post(tree.read(f"{pkg.path}/post.html")), "2026-10-06")
        items = ET.fromstring(tree.read(FEED)).findall("channel/item")
        self.assertEqual(items[0].findtext("title"), HEADLINE)
        self.assertEqual(items[0].findtext("description"), DESC)
        self.assertEqual(len(items), 2)


if __name__ == "__main__":
    unittest.main()

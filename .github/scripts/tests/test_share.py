import unittest

from blogpub.share import add_share_bar, share_bar

URL = "https://www.klaritydisk.com/blog/test-post"
PAGE = '<main>\n  <div class="article-body">x</div>\n\n  <div class="article-cta">\n    CTA\n  </div>\n</main>\n'


class ShareTest(unittest.TestCase):
    def test_links_are_encoded(self):
        bar = share_bar(URL, "What's taking space? A & B")
        self.assertIn("https://x.com/intent/post?text=What%27s%20taking%20space%3F%20A%20%26%20B&amp;url=https%3A%2F%2Fwww.klaritydisk.com%2Fblog%2Ftest-post", bar)
        self.assertIn("https://wa.me/?text=", bar)
        self.assertIn("reddit.com/submit?url=", bar)
        self.assertIn("facebook.com/sharer/sharer.php?u=", bar)
        self.assertIn('data-title="What&#x27;s taking space? A &amp; B"', bar)

    def test_inserted_once_before_cta(self):
        page = add_share_bar(PAGE, URL, "T")
        self.assertLess(page.index('class="share-bar"'), page.index('class="article-cta"'))
        self.assertEqual(add_share_bar(page, URL, "T"), page)
        self.assertEqual(page.count("/js/share.js"), 1)

    def test_falls_back_to_related_posts(self):
        page = add_share_bar('<article>x</article>\n    <!-- Related Posts -->\n<div class="related-posts"></div>', URL, "T")
        self.assertLess(page.index('class="share-bar"'), page.index("Related Posts"))

    def test_no_anchor_raises(self):
        with self.assertRaises(ValueError):
            add_share_bar("<div>nothing</div>", URL, "T")

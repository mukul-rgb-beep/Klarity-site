import unittest

from blogpub.post import normalize, parse_post
from tests.helpers import DESC, FAQ, HEADLINE, make_post


class ParsePostTest(unittest.TestCase):
    def test_reads_head_schema_links_and_faq(self):
        m = parse_post(make_post())
        self.assertEqual(m.headline, HEADLINE)
        self.assertEqual(m.title_tag, f"<title>{HEADLINE} | Klarity Blog</title>")
        self.assertEqual(m.meta["description"], DESC)            # &#x27; decoded
        self.assertEqual(m.meta["og:description"], DESC)
        self.assertEqual(m.meta["twitter:description"], DESC)
        self.assertEqual(m.schema("BlogPosting")["description"], DESC)
        self.assertEqual(m.canonical, "https://www.klaritydisk.com/blog/test-post")
        self.assertEqual(m.schema_url, "https://www.klaritydisk.com/blog/test-post")
        self.assertIn(("https://www.klaritydisk.com/", "Mac disk space analyzer"), m.links)
        self.assertEqual(m.faq_visible, [tuple(p) for p in FAQ])
        self.assertEqual(m.jsonld_errors, [])

    def test_schema_url_accepts_id_object(self):
        html = make_post().replace('"mainEntityOfPage": "https://www.klaritydisk.com/blog/test-post"',
                                   '"mainEntityOfPage": {"@type": "WebPage", "@id": "https://x/y"}')
        self.assertEqual(parse_post(html).schema_url, "https://x/y")

    def test_bad_jsonld_is_recorded_not_raised(self):
        html = make_post().replace('"@type": "BreadcrumbList"', '"@type": BreadcrumbList')
        self.assertEqual(len(parse_post(html).jsonld_errors), 1)

    def test_normalize(self):
        self.assertEqual(normalize("  It&#x27;s <b>bold</b>\n  here "), "It's bold here")


if __name__ == "__main__":
    unittest.main()

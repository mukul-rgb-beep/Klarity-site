import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from blogpub.checks import check_package
from blogpub.package import load_packages
from blogpub.tree import Tree
from blogpub.xpost import TEXT_LIMIT, check_x_post, oauth_header, oauth_signature, weighted_length
from tests.helpers import DIRNAME, default_package, make_site

SCRIPT = Path(__file__).resolve().parents[1] / "post_to_x.py"


class XPostTest(unittest.TestCase):
    def test_signature_matches_x_documented_example(self):
        # The worked example in X's "Creating a signature" developer documentation.
        params = {"include_entities": "true", "status": "Hello Ladies + Gentlemen, a signed OAuth request!",
                  "oauth_consumer_key": "xvz1evFS4wEEPTGEFPHBog",
                  "oauth_nonce": "kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg",
                  "oauth_signature_method": "HMAC-SHA1", "oauth_timestamp": "1318622958",
                  "oauth_token": "370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb", "oauth_version": "1.0"}
        sig = oauth_signature("POST", "https://api.twitter.com/1.1/statuses/update.json", params,
                              "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw", "LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE")
        self.assertEqual(sig, "hCtSmYh+iHYCEqBWrE7C7hYmtUk=")

    def test_header_has_every_oauth_field(self):
        h = oauth_header("POST", "https://api.x.com/2/tweets", "k", "s", "t", "ts", nonce="n", timestamp="1")
        self.assertTrue(h.startswith("OAuth "))
        for f in ("oauth_consumer_key", "oauth_nonce", "oauth_signature", "oauth_signature_method",
                  "oauth_timestamp", "oauth_token", "oauth_version"):
            self.assertIn(f + '="', h)

    def test_weighted_length(self):
        self.assertEqual(weighted_length("abc"), 3)
        self.assertEqual(weighted_length("日本"), 4)
        self.assertEqual(weighted_length("📦"), 2)

    def test_check_x_post(self):
        self.assertEqual(check_x_post(None), [])
        self.assertEqual(check_x_post("Fine text."), [])
        self.assertTrue(check_x_post(""))
        self.assertTrue(check_x_post("see https://example.com"))
        self.assertEqual(check_x_post("a" * TEXT_LIMIT), [])
        self.assertTrue(check_x_post("a" * (TEXT_LIMIT + 1)))

    def test_package_check_reports_bad_x_post(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_site(Path(d))
            pkg = default_package() | {"x_post": "x" * 300}
            (root / "_scheduled" / DIRNAME / "package.json").write_text(json.dumps(pkg))
            tree = Tree(root)
            errs = check_package(tree, load_packages(tree)[0])
            self.assertTrue(any("x_post is 300" in e for e in errs), errs)

    def test_script_without_keys_exits_2(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("X_")}
        r = subprocess.run([sys.executable, str(SCRIPT), "hello"], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("X keys are not set", r.stderr)

    def test_script_dry_run_does_not_send(self):
        env = dict(os.environ, X_API_KEY="a", X_API_SECRET="b", X_ACCESS_TOKEN="c", X_ACCESS_SECRET="d")
        r = subprocess.run([sys.executable, str(SCRIPT), "hello", "--dry-run"], env=env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("would post", r.stdout)

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import publish
from tests.helpers import DIRNAME, default_package, make_package, make_site


class CliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_site(Path(self._tmp.name))
        self.report = Path(self._tmp.name) / "report.json"

    def tearDown(self):
        self._tmp.cleanup()

    def run_cli(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            code = publish.main(["--root", str(self.root), *argv, "--report", str(self.report)])
        return code, out.getvalue(), json.loads(self.report.read_text())

    def test_check_passes_and_fails(self):
        code, _, rep = self.run_cli("check")
        self.assertEqual((code, rep), (0, {"packages": [DIRNAME], "errors": {}}))
        (self.root / "blog" / "a.html").write_text("gone")
        code, out, rep = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn(DIRNAME, rep["errors"])
        self.assertIn("matches 0 times", out)

    def test_not_due_does_nothing(self):
        code, _, rep = self.run_cli("publish", "--date", "2026-10-05")
        self.assertEqual((code, rep["published"]), (0, []))
        self.assertFalse((self.root / "blog" / "test-post.html").exists())

    def test_dry_run_prints_diff_and_writes_nothing(self):
        code, out, rep = self.run_cli("publish", "--date", "2026-10-06", "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("+/blog/test-post.html /blog/test-post 301", out)
        self.assertEqual(rep["published"][0]["slug"], "test-post")
        self.assertFalse((self.root / "blog" / "test-post.html").exists())

    def test_publish_writes_and_reports(self):
        code, _, rep = self.run_cli("publish", "--date", "2026-10-06")
        self.assertEqual(code, 0)
        self.assertTrue((self.root / "blog" / "test-post.html").exists())
        self.assertFalse((self.root / "_scheduled" / DIRNAME).exists())
        self.assertTrue((self.root / "_scheduled" / "README.md").exists())
        p = rep["published"][0]
        self.assertEqual(p["title_tag"], "<title>Find Old Files You Forgot About on Your Mac | Klarity Blog</title>")
        self.assertEqual(len(p["inbound_urls"]), 4)
        self.assertIsNone(p["requires"])

    def gated(self, requires):
        data = default_package()
        data["requires"] = requires
        (self.root / "_scheduled" / DIRNAME / "package.json").write_text(json.dumps(data))

    def test_gate_holds_until_version(self):
        self.gated("1.3.1")
        code, _, rep = self.run_cli("publish", "--date", "2026-10-06", "--live-version", "1.3")
        self.assertEqual((code, rep["published"]), (0, []))
        self.assertEqual(rep["held"][0]["requires"], "1.3.1")
        code, _, rep = self.run_cli("publish", "--date", "2026-10-06", "--live-version", "1.3.1")
        self.assertEqual(len(rep["published"]), 1)

    def test_failed_lookup_holds_gated_but_publishes_others(self):
        self.gated("1.3.1")
        make_package(self.root, "2026-10-01-other", package=default_package("other", "2026-10-01"))
        # 'other' rewrites the same find texts; give it its own sentences
        for name in ("a", "b", "c", "treemap-icicle-vs-sunburst"):
            f = self.root / "blog" / f"{name}.html"
            f.write_text(f.read_text().replace("</p>", f"</p><p>Other in {name}.</p>"))
        data = default_package("other", "2026-10-01")
        for link, name in zip(data["inbound_links"], ("treemap-icicle-vs-sunburst", "a", "b", "c")):
            link["find"] = f"Other in {name}."
            link["replace"] = f'Other in <a href="/blog/other">{name}</a>.'
        (self.root / "_scheduled" / "2026-10-01-other" / "package.json").write_text(json.dumps(data))
        code, _, rep = self.run_cli("publish", "--date", "2026-10-06", "--live-version", "")
        self.assertEqual(code, 0)
        self.assertEqual([p["slug"] for p in rep["published"]], ["other"])
        self.assertEqual([h["dirname"] for h in rep["held"]], [DIRNAME])

    def test_invalid_due_package_writes_nothing(self):
        (self.root / "blog" / "a.html").write_text("gone")
        before = (self.root / "sitemap.xml").read_text()
        code, _, rep = self.run_cli("publish", "--date", "2026-10-06")
        self.assertEqual(code, 1)
        self.assertIn(DIRNAME, rep["errors"])
        self.assertEqual((self.root / "sitemap.xml").read_text(), before)
        self.assertFalse((self.root / "blog" / "test-post.html").exists())

    def test_version_at_least(self):
        v = publish.version_at_least
        self.assertTrue(v("1.3.1", "1.3.1"))
        self.assertTrue(v("1.4", "1.3.1"))
        self.assertFalse(v("1.3", "1.3.1"))
        self.assertFalse(v("", "1.3.1"))
        self.assertFalse(v(None, "1.3.1"))
        self.assertFalse(v("1.3b", "1.3.1"))


if __name__ == "__main__":
    unittest.main()

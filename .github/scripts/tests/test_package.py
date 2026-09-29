import json
import tempfile
import unittest
from pathlib import Path

from blogpub.package import load_packages
from blogpub.tree import Tree
from tests.helpers import DIRNAME, default_package, make_package, make_site


class LoadPackagesTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_site(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def load(self):
        return load_packages(Tree(self.root))

    def test_valid_package(self):
        [p] = self.load()
        self.assertEqual((p.dirname, p.slug, p.publish_date, p.requires), (DIRNAME, "test-post", "2026-10-06", None))
        self.assertEqual(p.path, f"_scheduled/{DIRNAME}")
        self.assertEqual(p.url, "https://www.klaritydisk.com/blog/test-post")
        self.assertEqual(len(p.inbound_links), 4)
        self.assertEqual(p.errors, [])

    def test_sorted_by_date(self):
        make_package(self.root, "2026-10-01-early")
        self.assertEqual([p.dirname for p in self.load()], ["2026-10-01-early", DIRNAME])

    def test_bad_folder_name(self):
        make_package(self.root, "2026-10-13-Bad_Name", package=default_package("Bad_Name", "2026-10-13"))
        bad = [p for p in self.load() if p.dirname.endswith("Bad_Name")][0]
        self.assertTrue(any("folder name" in e for e in bad.errors))

    def test_folder_must_match_json(self):
        make_package(self.root, "2026-10-13-other", package=default_package("other", "2026-10-20"))
        bad = [p for p in self.load() if p.dirname == "2026-10-13-other"][0]
        self.assertTrue(any("does not match" in e for e in bad.errors))

    def test_missing_or_broken_json(self):
        (self.root / "_scheduled" / DIRNAME / "package.json").write_text("{nope")
        self.assertTrue(any("does not parse" in e for e in self.load()[0].errors))
        (self.root / "_scheduled" / DIRNAME / "package.json").unlink()
        self.assertTrue(any("missing" in e for e in self.load()[0].errors))

    def test_bad_date_and_bad_link(self):
        data = default_package()
        data["publish_date"] = "20261006"
        data["inbound_links"].append({"file": "blog/a.html"})
        (self.root / "_scheduled" / DIRNAME / "package.json").write_text(json.dumps(data))
        errs = self.load()[0].errors
        self.assertTrue(any("not YYYY-MM-DD" in e for e in errs))
        self.assertTrue(any("inbound_links[4]" in e for e in errs))

    def test_readme_is_not_a_package(self):
        self.assertEqual(len(self.load()), 1)


if __name__ == "__main__":
    unittest.main()

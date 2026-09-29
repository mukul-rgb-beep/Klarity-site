import tempfile
import unittest
from pathlib import Path

from blogpub import url_for
from blogpub.tree import Tree


class TreeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "a.txt").write_text("one\n")
        (self.root / "pkg" / "x").mkdir(parents=True)
        (self.root / "pkg" / "x" / "f.html").write_text("f\n")
        (self.root / "pkg" / "x" / ".DS_Store").write_bytes(b"\0")
        self.tree = Tree(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def test_overlay_does_not_touch_disk_until_commit(self):
        self.tree.write("a.txt", "two\n")
        self.assertEqual(self.tree.read("a.txt"), "two\n")
        self.assertEqual((self.root / "a.txt").read_text(), "one\n")
        self.tree.commit()
        self.assertEqual((self.root / "a.txt").read_text(), "two\n")

    def test_delete_hides_file_and_commit_removes_empty_dirs(self):
        for f in self.tree.files_under("pkg/x"):
            self.tree.delete(f)
        self.assertFalse(self.tree.exists("pkg/x/f.html"))
        self.assertEqual(self.tree.subdirs("pkg"), [])
        self.tree.commit()
        self.assertFalse((self.root / "pkg" / "x" / "f.html").exists())

    def test_files_under_ignores_dotfiles(self):
        self.assertEqual(self.tree.files_under("pkg/x"), ["pkg/x/f.html"])
        self.assertEqual(self.tree.subdirs("pkg"), ["x"])

    def test_diff_lists_every_change(self):
        self.tree.write("a.txt", "two\n")
        self.tree.write("new.txt", "hi\n")
        self.tree.write("img.png", b"\x89PNG")
        self.tree.delete("pkg/x/f.html")
        d = self.tree.diff()
        self.assertIn("-one", d)
        self.assertIn("+two", d)
        self.assertIn("+hi", d)
        self.assertIn("binary: img.png", d)
        self.assertIn("deleted: pkg/x/f.html", d)

    def test_fork_is_independent(self):
        other = self.tree.fork()
        other.write("a.txt", "fork\n")
        self.assertEqual(self.tree.read("a.txt"), "one\n")

    def test_preserves_crlf(self):
        (self.root / "crlf.txt").write_bytes(b"x\r\n")
        self.assertEqual(self.tree.read("crlf.txt"), "x\r\n")

    def test_url_for(self):
        self.assertEqual(url_for("blog/a.html"), "https://www.klaritydisk.com/blog/a")
        self.assertEqual(url_for("press.html"), "https://www.klaritydisk.com/press")
        self.assertEqual(url_for("blog/index.html"), "https://www.klaritydisk.com/blog/")
        self.assertEqual(url_for("index.html"), "https://www.klaritydisk.com/")


if __name__ == "__main__":
    unittest.main()

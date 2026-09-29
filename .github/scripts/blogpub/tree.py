"""A read-through overlay on a directory: writes stay in memory until commit()."""
from __future__ import annotations

import difflib
from pathlib import Path

_DELETED = object()


class Tree:
    def __init__(self, root):
        self.root = Path(root)
        self._changes: dict[str, object] = {}

    def fork(self) -> "Tree":
        other = Tree(self.root)
        other._changes = dict(self._changes)
        return other

    def exists(self, rel: str) -> bool:
        if rel in self._changes:
            return self._changes[rel] is not _DELETED
        return (self.root / rel).is_file()

    def read_bytes(self, rel: str) -> bytes:
        v = self._changes.get(rel)
        if v is _DELETED:
            raise FileNotFoundError(rel)
        if v is not None:
            return v if isinstance(v, bytes) else v.encode("utf-8")
        return (self.root / rel).read_bytes()

    def read(self, rel: str) -> str:
        v = self._changes.get(rel)
        if v is _DELETED:
            raise FileNotFoundError(rel)
        if v is not None:
            return v if isinstance(v, str) else v.decode("utf-8")
        with open(self.root / rel, encoding="utf-8", newline="") as f:
            return f.read()

    def write(self, rel: str, content) -> None:
        self._changes[rel] = content

    def delete(self, rel: str) -> None:
        self._changes[rel] = _DELETED

    def files_under(self, rel: str) -> list[str]:
        """Every non-dot file below rel, as repo-relative posix paths, overlay applied."""
        found = set()
        base = self.root / rel
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_file() and not p.name.startswith("."):
                    found.add(p.relative_to(self.root).as_posix())
        for k, v in self._changes.items():
            if k.startswith(rel + "/") and not k.rsplit("/", 1)[1].startswith("."):
                if v is _DELETED:
                    found.discard(k)
                else:
                    found.add(k)
        return sorted(found)

    def subdirs(self, rel: str) -> list[str]:
        """Names of the directories directly below rel that still hold at least one file."""
        base = self.root / rel
        if not base.is_dir():
            return []
        return sorted(d.name for d in base.iterdir()
                      if d.is_dir() and self.files_under(f"{rel}/{d.name}"))

    def changed_paths(self) -> list[str]:
        return sorted(self._changes)

    def diff(self) -> str:
        out = []
        for rel in self.changed_paths():
            v = self._changes[rel]
            if v is _DELETED:
                out.append(f"deleted: {rel}\n")
            elif isinstance(v, bytes):
                out.append(f"binary: {rel} ({len(v)} bytes)\n")
            else:
                disk = self.root / rel
                old = disk.read_text(encoding="utf-8") if disk.is_file() else ""
                out.extend(difflib.unified_diff(old.splitlines(True), v.splitlines(True),
                                                f"a/{rel}", f"b/{rel}"))
        return "".join(out)

    def commit(self) -> None:
        for rel, v in sorted(self._changes.items()):
            path = self.root / rel
            if v is _DELETED:
                if path.is_file():
                    path.unlink()
                parent = path.parent
                while parent != self.root and parent.is_dir():
                    leftovers = [p for p in parent.iterdir() if p.name != ".DS_Store"]
                    if leftovers:
                        break
                    for p in parent.iterdir():
                        p.unlink()
                    parent.rmdir()
                    parent = parent.parent
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(v, bytes):
                    path.write_bytes(v)
                else:
                    with open(path, "w", encoding="utf-8", newline="") as f:
                        f.write(v)
        self._changes.clear()

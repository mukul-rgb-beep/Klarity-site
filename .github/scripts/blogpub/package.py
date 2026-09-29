"""A queued post: _scheduled/<YYYY-MM-DD>-<slug>/{package.json, post.html, card.html, assets/}."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date

from blogpub import SCHEDULED, SITE

DIR_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERSION_RE = re.compile(r"^\d+(\.\d+)*$")


@dataclass
class InboundLink:
    file: str
    find: str
    replace: str


@dataclass
class Package:
    dirname: str
    slug: str = ""
    publish_date: str = ""
    requires: str | None = None
    inbound_links: list[InboundLink] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def path(self) -> str:
        return f"{SCHEDULED}/{self.dirname}"

    @property
    def url(self) -> str:
        return f"{SITE}/blog/{self.slug}"


def load_package(tree, dirname: str) -> Package:
    pkg = Package(dirname)
    m = DIR_RE.match(dirname)
    if not m:
        pkg.errors.append("folder name must be YYYY-MM-DD-<slug>, slug in lowercase letters, digits and hyphens")
    try:
        data = json.loads(tree.read(f"{pkg.path}/package.json"))
    except FileNotFoundError:
        pkg.errors.append("package.json is missing")
        return pkg
    except json.JSONDecodeError as e:
        pkg.errors.append(f"package.json does not parse: {e}")
        return pkg
    if not isinstance(data, dict):
        pkg.errors.append("package.json must be a JSON object")
        return pkg
    pkg.slug = str(data.get("slug") or "")
    pkg.publish_date = str(data.get("publish_date") or "")
    pkg.requires = data.get("requires")
    if pkg.requires is not None and not (isinstance(pkg.requires, str) and VERSION_RE.match(pkg.requires)):
        pkg.errors.append(f"requires {pkg.requires!r} must be null or a version string such as \"1.3.1\"")
        pkg.requires = None
    try:
        if not DATE_RE.match(pkg.publish_date):
            raise ValueError
        date.fromisoformat(pkg.publish_date)
    except ValueError:
        pkg.errors.append(f"publish_date {pkg.publish_date!r} is not YYYY-MM-DD")
    if m and (m.group(1), m.group(2)) != (pkg.publish_date, pkg.slug):
        pkg.errors.append(f"folder name {dirname} does not match publish_date {pkg.publish_date!r} and slug {pkg.slug!r}")
    for i, link in enumerate(data.get("inbound_links") or []):
        try:
            pkg.inbound_links.append(InboundLink(link["file"], link["find"], link["replace"]))
        except (KeyError, TypeError):
            pkg.errors.append(f"inbound_links[{i}] needs file, find and replace")
    return pkg


def load_packages(tree) -> list[Package]:
    pkgs = [load_package(tree, d) for d in tree.subdirs(SCHEDULED)]
    return sorted(pkgs, key=lambda p: (p.publish_date or "9999-99-99", p.dirname))

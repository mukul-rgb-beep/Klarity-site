#!/usr/bin/env python3
"""Validate and publish queued blog posts. See _scheduled/README.md."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from blogpub.apply import apply_package  # noqa: E402
from blogpub.checks import check_all  # noqa: E402
from blogpub.package import load_packages  # noqa: E402
from blogpub.post import parse_post  # noqa: E402
from blogpub.tree import Tree  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]


def version_at_least(live: str | None, required: str) -> bool:
    try:
        a = [int(x) for x in (live or "").split(".")]
        b = [int(x) for x in required.split(".")]
    except ValueError:
        return False
    n = max(len(a), len(b))
    return a + [0] * (n - len(a)) >= b + [0] * (n - len(b))


def _headline(tree, pkg) -> str:
    try:
        return parse_post(tree.read(f"{pkg.path}/post.html")).headline
    except FileNotFoundError:
        return pkg.dirname


def _print_errors(errors: dict[str, list[str]]) -> None:
    for dirname, errs in errors.items():
        for e in errs:
            print(f"{dirname}: {e}")


def _write(report: str | None, data: dict) -> None:
    if report:
        Path(report).write_text(json.dumps(data, indent=2) + "\n")


def cmd_check(args) -> int:
    tree = Tree(args.root)
    pkgs = load_packages(tree)
    errors = {k: v for k, v in check_all(tree, pkgs).items() if v}
    _write(args.report, {"packages": [p.dirname for p in pkgs], "errors": errors})
    _print_errors(errors)
    print(f"{len(pkgs)} package(s) queued, {len(errors)} with problems")
    return 1 if errors else 0


def cmd_publish(args) -> int:
    tree = Tree(args.root)
    due = [p for p in load_packages(tree) if p.publish_date and p.publish_date <= args.date]
    held = [p for p in due if p.requires and not version_at_least(args.live_version, p.requires)]
    ready = [p for p in due if p not in held]
    report = {"published": [], "errors": {},
              "held": [{"dirname": p.dirname, "headline": _headline(tree, p), "requires": p.requires} for p in held]}
    errors = {k: v for k, v in check_all(tree, ready).items() if v}
    if errors:
        report["errors"] = errors
        _write(args.report, report)
        _print_errors(errors)
        print("Nothing published: fix the problems above.")
        return 1
    for pkg in ready:
        meta = parse_post(tree.read(f"{pkg.path}/post.html"))
        inbound = apply_package(tree, pkg, meta, args.date)
        report["published"].append({"dirname": pkg.dirname, "slug": pkg.slug, "headline": meta.headline,
                                    "url": pkg.url, "title_tag": meta.title_tag, "inbound_urls": inbound,
                                    "requires": pkg.requires})
    if args.dry_run:
        print(tree.diff())
    else:
        tree.commit()
    _write(args.report, report)
    for p in report["published"]:
        print(f"{'would publish' if args.dry_run else 'published'}: {p['url']}")
    for h in report["held"]:
        print(f"held until Klarity {h['requires']}: {h['dirname']}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="publish.py")
    ap.add_argument("--root", default=str(REPO_ROOT))
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--report")
    p = sub.add_parser("publish")
    p.add_argument("--date", required=True)
    p.add_argument("--live-version", default="")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--report")
    args = ap.parse_args(argv)
    return cmd_check(args) if args.cmd == "check" else cmd_publish(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

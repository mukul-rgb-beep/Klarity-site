#!/usr/bin/env python3
"""Blog index art: treemap mosaics in Klarity's age colours, written into css/site.css.

  blog_art.py           -> rewrites the rules between the BLOG-ART markers in css/site.css
  blog_art.py --check   -> exit 1 if css/site.css is not what this script would write

The header gets one soft mosaic; each blog card gets one of 12 small ones, chosen by
:nth-last-child so a card keeps its art when new posts are inserted above it.
Seeds are fixed, so the output only changes when this file does. Bump the ?v= on every
page's site.css link after regenerating.
"""
import random
import sys
import urllib.parse
from pathlib import Path

CSS = Path(__file__).resolve().parents[2] / "css" / "site.css"
START, END = "/* BLOG-ART:START */", "/* BLOG-ART:END */"

AGE = ["#5B8FD6", "#74AB84", "#B9A45E", "#D38A4E", "#C8644F"]  # AgeStep: month, year, 1-2, 2-3, 3+ years

# Each card variant leans on one or two age steps so neighbouring cards differ.
CARD_WEIGHTS = [
    [8, 3, 1, 1, 1], [2, 8, 2, 1, 1], [1, 2, 8, 3, 1], [1, 1, 3, 8, 2],
    [3, 1, 1, 2, 7], [3, 4, 3, 2, 2], [6, 6, 1, 1, 1], [1, 3, 6, 6, 1],
    [5, 1, 1, 1, 5], [1, 6, 1, 1, 4], [4, 2, 5, 1, 1], [2, 2, 2, 5, 4],
]


def squarify(vals, x, y, w, h):
    """Squarified treemap of vals (sorted descending, summing to w*h) -> [(x, y, w, h)]."""
    out, vals = [], list(vals)
    while vals:
        short = min(w, h)
        row, best = [], float("inf")
        while vals:
            cand = row + [vals[0]]
            s = sum(cand)
            worst = max(max(short * short * v / (s * s), (s * s) / (short * short * v)) for v in cand)
            if worst > best:
                break
            row, best = cand, worst
            vals.pop(0)
        s = sum(row)
        if w >= h:
            cw, cy = s / h, y
            for v in row:
                out.append((x, cy, cw, v / cw))
                cy += v / cw
            x, w = x + cw, w - cw
        else:
            ch, cx = s / w, x
            for v in row:
                out.append((cx, y, v / ch, ch))
                cx += v / ch
            y, h = y + ch, h - ch
    return out


def mute(hexc, k):
    """Mix a #RRGGBB colour toward white by k (0..1)."""
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(round(c + (255 - c) * k) for c in (r, g, b))


def mosaic(seed, W, H, n, weights, gap, rx, sheen, split=0, mix=0.0, bg=None):
    """A treemap of n tiles as a CSS url() holding an SVG data URI."""
    rnd = random.Random(seed)
    raw = sorted((rnd.paretovariate(1.1) for _ in range(n)), reverse=True)
    tot = sum(raw)
    parts = []
    for i, (x, y, w, h) in enumerate(squarify([v / tot * W * H for v in raw], 0, 0, W, H)):
        col = rnd.choices(AGE, weights)[0]
        tiles = [(x, y, w, h)]
        if i < split and w > 60 and h > 60:  # split the biggest tiles once so they read as nested folders
            sub = sorted((rnd.paretovariate(1.3) for _ in range(rnd.randint(3, 6))), reverse=True)
            st = sum(sub)
            tiles = squarify([v / st * w * h for v in sub], x, y, w, h)
        for (tx, ty, tw, th) in tiles:
            if tw - gap < 2 or th - gap < 2:
                continue
            c = col if len(tiles) == 1 else rnd.choices(AGE, [weights[j] + (6 if AGE[j] == col else 0) for j in range(5)])[0]
            parts.append(f"<rect x='{tx + gap / 2:.1f}' y='{ty + gap / 2:.1f}' width='{tw - gap:.1f}' height='{th - gap:.1f}' rx='{rx}' fill='{mute(c, mix)}'/>")
    body = (f"<rect width='{W}' height='{H}' fill='{bg}'/>" if bg else "") + "".join(parts)
    defs = ""
    if sheen:  # the app's tile finish: a light top, a slightly darker foot
        defs = ("<defs><linearGradient id='s' x1='0' y1='0' x2='0' y2='1'>"
                "<stop offset='0' stop-color='#fff' stop-opacity='.22'/>"
                "<stop offset='.55' stop-color='#fff' stop-opacity='0'/>"
                "<stop offset='1' stop-color='#000' stop-opacity='.06'/></linearGradient></defs>")
        body += f"<rect width='{W}' height='{H}' fill='url(#s)'/>"
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' preserveAspectRatio='xMidYMid slice'>{defs}{body}</svg>"
    return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe=" =:/,.-'<>()") + '")'


def rules():
    lines = [START, "body>header::before{background-image:%s}" % mosaic(7, 1600, 460, 26, [5, 4, 3, 3, 3], 10, 12, False, split=3)]
    for i, w in enumerate(CARD_WEIGHTS):
        nth = f"12n+{i + 1}" if i + 1 < 12 else "12n"
        art = mosaic(100 + i, 400, 150, 13, w, 3, 3, True, split=3, mix=0.18, bg="#FFFFFF")
        lines.append(f".blog-card:nth-last-child({nth})::before{{background-image:{art}}}")
    lines.append(END)
    return "\n".join(lines)


def main():
    css = CSS.read_text()
    a, b = css.index(START), css.index(END) + len(END)
    new = css[:a] + rules() + css[b:]
    if "--check" in sys.argv:
        if new != css:
            print("css/site.css blog art is stale: run .github/scripts/blog_art.py")
            sys.exit(1)
        print("blog art up to date")
        return
    CSS.write_text(new)
    print("wrote blog art into", CSS)


if __name__ == "__main__":
    main()

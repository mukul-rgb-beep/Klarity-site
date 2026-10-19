#!/usr/bin/env python3
"""Blog card illustrations: one small scene per post, drawn in macOS's own vocabulary
(a Storage bar, a Finder list, a drive, a sheet) in the app's age colours.

  card_art.py           -> writes card-<slug>.svg for every post in ART: live posts into blog/,
                           queued posts into their package's assets/ (published to blog/ on the day)
  card_art.py --check   -> exit 1 if any written file differs from what this script would write

The blog index shows /blog/card-<slug>.svg at the top of each card. A new post needs an entry
in ART below (a 320x180 scene) and the card-art line in its card.html.
"""
import math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Palette: the app's five age steps, system greys, ink, accent.
AGE = ["#5B8FD6", "#74AB84", "#B9A45E", "#D38A4E", "#C8644F"]
INK, INK2, INK3 = "#1D1D1F", "#6E6E73", "#AEAEB2"
GREY, GREY2, TRACK = "#C7C7CC", "#D9D9DE", "#ECECF0"
ACCENT = "#0E7C86"
FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif"

DEFS = f"""<defs>
<filter id="sh" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="5" stdDeviation="7" flood-color="#1C2030" flood-opacity=".13"/><feDropShadow dx="0" dy="1" stdDeviation="1" flood-color="#1C2030" flood-opacity=".08"/></filter>
<linearGradient id="ai" x1="0" x2="1"><stop offset="0" stop-color="#5B8FD6"/><stop offset=".35" stop-color="#8E7FD0"/><stop offset=".7" stop-color="#D3779B"/><stop offset="1" stop-color="#D38A4E"/></linearGradient>
</defs>"""

def svg(body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180" width="320" height="180" role="img" '
            f'aria-label="{label}" font-family="{FONT}">{DEFS}{body}</svg>\n')

def win(x, y, w, h, r=10, fill="#fff"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" filter="url(#sh)"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="#000" stroke-opacity=".09" stroke-width=".75"/>')

def text(x, y, s, size=13, weight=400, fill=INK, anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>'

def bar(x, y, w, h, segs, r=None):
    """Segmented capsule. segs = [(width, fill)]; clipped to a rounded track."""
    r = h / 2 if r is None else r
    cid = f"c{x}{y}{w}".replace(".", "")
    out = [f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{TRACK}"/><g clip-path="url(#{cid})">']
    cx = x
    for sw, f in segs:
        out.append(f'<rect x="{cx}" y="{y}" width="{sw}" height="{h}" fill="{f}"/>')
        cx += sw + 1.5
    out.append("</g>")
    return "".join(out)

def sparkle(cx, cy, s, fill="url(#ai)"):
    p = (f"M{cx},{cy-s} C{cx+s*.18},{cy-s*.18} {cx+s*.18},{cy-s*.18} {cx+s},{cy} "
         f"C{cx+s*.18},{cy+s*.18} {cx+s*.18},{cy+s*.18} {cx},{cy+s} "
         f"C{cx-s*.18},{cy+s*.18} {cx-s*.18},{cy+s*.18} {cx-s},{cy} "
         f"C{cx-s*.18},{cy-s*.18} {cx-s*.18},{cy-s*.18} {cx},{cy-s}Z")
    return f'<path d="{p}" fill="{fill}"/>'

def dot(cx, cy, fill, r=4.5):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'

def folder(x, y, s=1.0, fill="#6AA6E8"):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M0 6a6 6 0 0 1 6-6h16l6 6h24a6 6 0 0 1 6 6v30a6 6 0 0 1-6 6H6a6 6 0 0 1-6-6Z" fill="{fill}"/>'
            f'<path d="M0 14a6 6 0 0 1 6-6h46a6 6 0 0 1 6 6v28a6 6 0 0 1-6 6H6a6 6 0 0 1-6-6Z" fill="#8DBDF0"/></g>')

def star(cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * .45
        pts.append(f"{cx + rr*math.cos(a):.1f},{cy + rr*math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke-linejoin="round"/>'

def treemap(x, y, w, h, tiles, gap=3, r=4):
    """tiles = [(fx, fy, fw, fh, fill)] as fractions of the box."""
    out = []
    for fx, fy, fw, fh, f in tiles:
        out.append(f'<rect x="{x+fx*w+gap/2:.1f}" y="{y+fy*h+gap/2:.1f}" width="{fw*w-gap:.1f}" height="{fh*h-gap:.1f}" rx="{r}" fill="{f}"/>')
    return "".join(out)

ART = {}

ART["apple-intelligence-storage-mac"] = svg(
    win(24, 42, 272, 96)
    + text(44, 70, "macOS", 16, 600)
    + bar(44, 82, 232, 12, [(84, GREY), (72, "url(#ai)"), (20, GREY2)])
    + sparkle(51, 117, 6.5) + text(64, 122, "Apple Intelligence", 14, 500)
    + text(276, 122, "29.45 GB", 14, 600, INK, "end"),
    "Storage settings: Apple Intelligence takes 29.45 GB of macOS storage")

dots = []
for i in range(28):
    cx, cy = 182 + (i % 7) * 15, 82 + (i // 7) * 17
    dots.append(f'<circle cx="{cx}" cy="{cy}" r="7.5" fill="{ACCENT}"/>' if i == 16 else f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="{GREY}"/>')
rc = 2 * math.pi * 33
ART["living-with-256gb-mac"] = svg(
    win(28, 32, 116, 116) + f'<circle cx="86" cy="90" r="33" fill="none" stroke="{TRACK}" stroke-width="9"/>'
    + f'<circle cx="86" cy="90" r="33" fill="none" stroke="{AGE[3]}" stroke-width="9" stroke-linecap="round" stroke-dasharray="{rc*.88:.1f} {rc:.1f}" transform="rotate(-90 86 90)"/>'
    + text(86, 92, "256", 17, 600, INK, "middle") + text(86, 106, "GB", 11, 500, INK2, "middle")
    + win(160, 32, 132, 116) + text(176, 60, "Every month", 13, 600) + "".join(dots),
    "A 256 GB disk at 88 percent and a monthly check on the calendar")

ART["external-drive-full-mac"] = svg(
    '<path d="M136 104 C 156 104, 152 90, 170 90" fill="none" stroke="#8E8E93" stroke-width="4" stroke-linecap="round"/>'
    + '<rect x="26" y="58" width="112" height="72" rx="14" fill="#3A3A3C" filter="url(#sh)"/>'
    + f'<circle cx="124" cy="118" r="2.6" fill="{AGE[1]}"/>' + text(42, 82, "5 TB", 14, 600, "#F5F5F7")
    + win(170, 46, 128, 92) + text(186, 72, "Backup", 14, 600)
    + bar(186, 84, 96, 10, [(30, AGE[0]), (24, AGE[1]), (20, AGE[2]), (20, AGE[4])])
    + text(186, 120, "85 GB free", 13, 600, AGE[4]),
    "An external 5 TB drive nearly full, with 85 GB free")

pale = ["#DDE6F3", "#E1ECE4", "#ECE6D3", "#E8E3EC", "#E4E9EF"]
ART["find-old-files-on-mac"] = svg(
    win(24, 20, 272, 140)
    + treemap(32, 28, 256, 124, [
        (0, 0, .56, .74, AGE[4]), (0, .74, .28, .26, pale[0]), (.28, .74, .28, .26, pale[1]),
        (.56, 0, .26, .42, pale[2]), (.82, 0, .18, .42, pale[0]), (.56, .42, .2, .58, pale[1]),
        (.76, .42, .24, .3, pale[3]), (.76, .72, .24, .28, pale[2])])
    + text(44, 54, "Travel Film 2023", 14, 600, "#1F0806") + text(44, 72, "40.8 GB · 3+ yrs", 12, 500, "#1F0806", extra='opacity=".8"'),
    "A treemap where one big red folder, untouched for over three years, stands out")

ART["klarity-disk-macworld-review"] = svg(
    win(76, 26, 168, 128)
    + text(98, 90, "4", 46, 600) + text(126, 90, "/ 5", 18, 500, INK2)
    + "".join(star(106 + i * 25, 120, 9.5, AGE[3] if i < 4 else TRACK) for i in range(5)),
    "A four out of five star review")

ART["how-much-space-for-macos-27"] = svg(
    win(24, 40, 272, 100)
    + text(44, 68, "macOS 27", 16, 600)
    + bar(44, 82, 232, 12, [(124, AGE[3])])
    + f'<line x1="214" y1="74" x2="214" y2="102" stroke="{INK}" stroke-width="1.5" stroke-dasharray="3 3"/>'
    + text(44, 122, "Free", 13, 500, INK2) + text(214, 122, "40 GB needed", 13, 600, INK, "middle"),
    "Free space falling short of the 40 GB macOS 27 needs to install")

lens = treemap(200, 78, 72, 72, [(0, 0, .55, .6, AGE[0]), (.55, 0, .45, .35, AGE[4]), (.55, .35, .45, .25, AGE[2]),
                                 (0, .6, .35, .4, AGE[1]), (.35, .6, .65, .4, AGE[3])], 3, 3)
ART["mac-storage-full-after-update"] = svg(
    win(20, 40, 250, 78)
    + text(40, 68, "Macintosh HD", 15, 600)
    + bar(40, 82, 210, 12, [(30, AGE[0]), (22, AGE[1]), (160, GREY)])
    + '<clipPath id="lens"><circle cx="236" cy="114" r="34"/></clipPath>'
    + f'<circle cx="236" cy="114" r="34" fill="#fff" filter="url(#sh)"/><g clip-path="url(#lens)">{lens}</g>'
    + f'<circle cx="236" cy="114" r="34" fill="none" stroke="{INK}" stroke-width="4.5"/>'
    + f'<line x1="261" y1="139" x2="284" y2="162" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>',
    "A magnifier over the grey System Data bar shows the folders inside")

ART["klarity-1-3-one-time-disk-access"] = svg(
    win(36, 24, 248, 132, 12)
    + folder(56, 42, .62) + text(102, 56, "Allow Klarity to access", 13, 600) + text(102, 73, "Macintosh HD", 13, 600)
    + f'<rect x="96" y="112" width="70" height="26" rx="6" fill="{TRACK}"/>' + text(131, 129, "Not Now", 12, 500, INK, "middle")
    + f'<rect x="172" y="112" width="100" height="26" rx="6" fill="{ACCENT}"/>' + text(222, 129, "Grant Access…", 12, 600, "#fff", "middle"),
    "Klarity asking once for access to Macintosh HD")

rows = [("Trash and Downloads", True), ("Find what is big", True), ("Caches", True), ("Old backups", False)]
chk = []
for i, (lab, done) in enumerate(rows):
    y = 40 + i * 28
    chk.append(f'<rect x="76" y="{y}" width="17" height="17" rx="5" fill="{ACCENT}"/>'
               f'<path d="M80 {y+9} l3.3 3.3 l6.5 -7" fill="none" stroke="#fff" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/>'
               if done else f'<rect x="76.5" y="{y+.5}" width="16" height="16" rx="5" fill="#fff" stroke="{GREY}" stroke-width="1.2"/>')
    chk.append(text(104, y + 13, lab, 14, 500, INK2 if done else INK))
ART["how-to-clean-up-mac-storage"] = svg(win(56, 22, 208, 136) + "".join(chk),
    "A checklist for cleaning up Mac storage, safest steps first")

files = [("Screen Recording.mov", "5.46 GB", AGE[0]), ("Photos Export.zip", "3.90 GB", AGE[2]),
         ("Install macOS Tahoe", "2.80 GB", AGE[4]), ("Ubuntu.iso", "1.90 GB", AGE[3])]
lst = []
for i, (n, gb, c) in enumerate(files):
    y = 40 + i * 28
    if i == 0:
        lst.append(f'<rect x="34" y="{y-7}" width="252" height="26" rx="6" fill="#E6F1F2"/>')
    lst.append(f'<rect x="46" y="{y}" width="10" height="13" rx="2" fill="{c}"/>' + text(64, y + 11, n, 13, 500)
               + text(274, y + 11, gb, 13, 600, INK, "end"))
ART["how-to-find-large-files-on-mac"] = svg(win(26, 22, 268, 132) + "".join(lst), "A list of the largest files, biggest first")

ART["what-is-system-data-on-mac"] = svg(
    win(24, 16, 272, 52)
    + text(42, 39, "System Data", 14, 600) + bar(42, 50, 236, 8, [(236, GREY)])
    + f'<path d="M66 68 V96 M160 68 V96 M254 68 V96" stroke="{GREY}" stroke-width="1.5" stroke-dasharray="2 3"/>'
    + "".join(win(24 + i * 94, 96, 84, 66, 10) + f'<rect x="{36+i*94}" y="108" width="16" height="16" rx="4.5" fill="{AGE[k]}"/>'
              + text(36 + i * 94, 141, lab, 13, 600) + text(36 + i * 94, 155, sz, 11, 500, INK2)
              for i, (lab, sz, k) in enumerate([("Developer", "91 GB", 0), ("Caches", "9.7 GB", 2), ("Snapshots", "", 3)])),
    "The grey System Data bar broken into named parts: Developer, Caches, Snapshots")

arcs = []
cx, cy = 232, 90
for r0, r1, segs in [(16, 30, [(0, 150, AGE[0]), (150, 260, AGE[1]), (260, 360, AGE[3])]),
                     (32, 46, [(0, 70, AGE[0]), (70, 150, AGE[2]), (150, 210, AGE[1]), (210, 260, AGE[4]), (260, 330, AGE[3]), (330, 360, AGE[2])])]:
    for a0, a1, c in segs:
        def pt(r, a): return f"{cx + r*math.cos(math.radians(a-90)):.1f},{cy + r*math.sin(math.radians(a-90)):.1f}"
        large = 1 if a1 - a0 > 180 else 0
        arcs.append(f'<path d="M{pt(r1,a0+1)} A{r1},{r1} 0 {large} 1 {pt(r1,a1-1)} L{pt(r0,a1-1)} A{r0},{r0} 0 {large} 0 {pt(r0,a0+1)}Z" fill="{c}"/>')
ART["treemap-icicle-vs-sunburst"] = svg(
    win(24, 26, 128, 128)
    + treemap(32, 34, 112, 112, [(0, 0, .58, .62, AGE[0]), (.58, 0, .42, .38, AGE[1]), (.58, .38, .42, .24, AGE[2]),
                                 (0, .62, .3, .38, AGE[3]), (.3, .62, .38, .38, AGE[1]), (.68, .62, .32, .38, AGE[4])])
    + win(168, 26, 128, 128) + f'<circle cx="{cx}" cy="{cy}" r="13" fill="{TRACK}"/>' + "".join(arcs),
    "A treemap beside a sunburst chart")

ART["building-liquid-glass-ui-macos"] = svg(
    '<filter id="blur"><feGaussianBlur stdDeviation="14"/></filter>'
    + f'<g filter="url(#blur)"><circle cx="104" cy="78" r="50" fill="{AGE[0]}"/><circle cx="210" cy="118" r="46" fill="{AGE[3]}"/><circle cx="240" cy="56" r="32" fill="{AGE[1]}"/></g>'
    + '<rect x="62" y="42" width="196" height="96" rx="18" fill="#fff" fill-opacity=".42" stroke="#fff" stroke-opacity=".9" stroke-width="1.2" filter="url(#sh)"/>'
    + text(84, 84, ".glassEffect()", 17, 600) + text(84, 106, "on macOS 14", 13, 500, INK2),
    "A translucent glass panel over soft colour")

logo = ('<rect x="8" y="8" width="50" height="48" rx="5" fill="#3ECFCF"/><rect x="62" y="8" width="50" height="26" rx="5" fill="#5B8DEF"/>'
        '<rect x="62" y="38" width="50" height="18" rx="5" fill="#47E0B0"/><rect x="8" y="60" width="30" height="52" rx="5" fill="#5B8DEF"/>'
        '<rect x="42" y="60" width="24" height="52" rx="5" fill="#3ECFCF"/><rect x="70" y="60" width="42" height="28" rx="5" fill="#7BA4F7"/>'
        '<rect x="70" y="92" width="42" height="20" rx="5" fill="#3ECFCF"/>')
ART["why-i-built-klarity"] = svg(
    win(122, 24, 76, 76, 18) + f'<g transform="translate(128 30) scale(.533)">{logo}</g>'
    + text(160, 128, "Klarity", 16, 600, INK, "middle") + text(160, 147, "$6.99 on the Mac App Store", 12, 500, INK2, "middle"),
    "The Klarity app icon")

def target(slug):
    queued = sorted(ROOT.glob(f"_scheduled/*-{slug}"))
    return (queued[0] / "assets" if queued else ROOT / "blog") / f"card-{slug}.svg"


def main():
    stale = []
    for slug, s in ART.items():
        t = target(slug)
        if "--check" in sys.argv:
            if not t.exists() or t.read_text() != s:
                stale.append(str(t.relative_to(ROOT)))
            continue
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(s)
    if stale:
        print("card art is stale or missing: run .github/scripts/card_art.py\n  " + "\n  ".join(stale))
        sys.exit(1)
    print(("card art up to date: " if "--check" in sys.argv else "wrote card art: ") + f"{len(ART)} posts")


if __name__ == "__main__":
    main()

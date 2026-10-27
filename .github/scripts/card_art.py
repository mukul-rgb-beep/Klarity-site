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

# 10 Nov — free space dropped after an update: the used-space spike that settles
ART["free-space-dropped-after-macos-update"] = svg(
    win(24, 22, 272, 136)
    + text(42, 48, "Used space", 13, 600)
    + f'<line x1="42" y1="122" x2="278" y2="122" stroke="{GREY}" stroke-width="1.5" stroke-dasharray="3 4"/>'
    + f'<path d="M42 122 H96 C 112 122, 116 66, 134 66 C 152 66, 168 104, 200 108 S 250 110, 278 110 V122 H42Z" fill="{AGE[3]}" fill-opacity=".16"/>'
    + f'<path d="M42 122 H96 C 112 122, 116 66, 134 66 C 152 66, 168 104, 200 108 S 250 110, 278 110" fill="none" stroke="{AGE[3]}" stroke-width="3" stroke-linecap="round"/>'
    + f'<circle cx="134" cy="66" r="4.5" fill="{AGE[3]}"/>' + text(144, 61, "+150 GB", 13, 600)
    + text(278, 102, "+30 GB", 12, 600, INK2, "end")
    + text(96, 144, "Update", 11, 500, INK2, "middle") + text(278, 144, "Days later", 11, 500, INK2, "end"),
    "Used space spikes the day after a macOS update, then settles a little above where it started")

# 24 Nov — Time Capsule stopped working: hand-over to a new Time Machine drive
ART["time-capsule-macos-27"] = svg(
    # the old Time Capsule, faded, with a "no longer supported" badge
    '<g opacity=".55">'
    + f'<rect x="38" y="44" width="64" height="98" rx="16" fill="#F4F4F6" filter="url(#sh)"/>'
    + f'<rect x="38" y="44" width="64" height="98" rx="16" fill="none" stroke="#000" stroke-opacity=".12" stroke-width=".75"/>'
    + f'<circle cx="70" cy="128" r="2.6" fill="{AGE[3]}"/>' + text(70, 70, "Time", 11, 600, INK2, "middle")
    + text(70, 84, "Capsule", 11, 600, INK2, "middle") + '</g>'
    + f'<circle cx="100" cy="48" r="12" fill="{AGE[4]}"/>'
    + '<path d="M95.5 43.5 l9 9 M104.5 43.5 l-9 9" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>'
    # hand-over arrow
    + f'<path d="M118 94 H148" stroke="{GREY}" stroke-width="2" stroke-dasharray="4 4" stroke-linecap="round"/>'
    + f'<path d="M144 88 l7 6 l-7 6" fill="none" stroke="{GREY}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    # the new backup drive, with the Time Machine clock
    + win(160, 40, 136, 104)
    + f'<circle cx="190" cy="72" r="14" fill="none" stroke="{ACCENT}" stroke-width="3"/>'
    + f'<path d="M190 64 V72 L196 76" fill="none" stroke="{ACCENT}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
    + text(178, 112, "Time Machine", 14, 600) + text(178, 130, "New backup drive", 12, 500, INK2),
    "An old Time Capsule marked unsupported, handing over to a new Time Machine backup drive")

# Intel-based Apps list (System Settings › General › About › Details), 320x180 scene for card_art.py.
_rows = [("Label Printer", AGE[0]), ("Scanner Utility", AGE[2]), ("Photo Converter", AGE[4])]
_lst = []
for _i, (_n, _c) in enumerate(_rows):
    _y = 66 + _i * 30
    _lst.append(f'<rect x="44" y="{_y}" width="20" height="20" rx="5.5" fill="{_c}"/>'
                + text(74, _y + 15, _n, 14, 500)
                + f'<rect x="226" y="{_y+2}" width="50" height="17" rx="8.5" fill="{TRACK}"/>'
                + text(251, _y + 15, "Intel", 11, 600, INK2, "middle"))
    if _i < 2:
        _lst.append(f'<line x1="74" y1="{_y+25}" x2="276" y2="{_y+25}" stroke="#000" stroke-opacity=".07"/>')
ART["intel-apps-rosetta-macos-27"] = svg(
    win(28, 22, 264, 140)
    + text(44, 48, "Intel-based Apps", 15, 600)
    + "".join(_lst),
    "The Intel-based Apps list in System Settings")


# 2026-11-06-purgeable-space-mac
# 6 Nov — purgeable space: Finder's "Available" counts space that is not free yet
_pg_hatch = (f'<pattern id="pghatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             f'<rect width="6" height="6" fill="#F1E7C8"/><rect width="3" height="6" fill="{AGE[2]}"/></pattern>')
ART["purgeable-space-mac"] = svg(
    _pg_hatch
    + win(24, 22, 272, 136)
    + text(42, 48, "Macintosh HD", 15, 600)
    # Finder's figure: purgeable + free
    + f'<path d="M176 76 V70 H276 V76" fill="none" stroke="{INK2}" stroke-width="1.5"/>'
    + text(276, 63, "Available 62 GB", 12, 600, INK, "end")
    + bar(42, 82, 234, 14, [(132, GREY), (72, "url(#pghatch)")])
    # what is really free right now
    + f'<path d="M249 102 V108 H276 V102" fill="none" stroke="{ACCENT}" stroke-width="1.5"/>'
    + text(276, 124, "Free now 18 GB", 12, 600, ACCENT, "end")
    + f'<rect x="42" y="114" width="14" height="14" rx="3.5" fill="url(#pghatch)"/>'
    + text(63, 125, "Purgeable", 12, 500, INK2),
    "A disk bar where Finder's 62 GB available is mostly purgeable space, with only 18 GB free right now")

# 2026-11-10-docker-vm-disk-images-mac
# 10 Nov — Docker and VM disk images: a 64 GB reserved file that only uses 9 GB on disk
_dvm_icon = (f'<rect x="44" y="40" width="30" height="38" rx="5" fill="{TRACK}" stroke="#000" stroke-opacity=".12" stroke-width=".75"/>'
             f'<rect x="50" y="62" width="18" height="9" rx="2" fill="{AGE[0]}"/>')
_dvm_pages = "".join(f'<rect x="{44 + i * 15.5:.1f}" y="128" width="12" height="16" rx="2.5" fill="{AGE[0] if i < 2 else "none"}" '
                     f'stroke="{AGE[0] if i < 2 else GREY}" stroke-width="1.2"{"" if i < 2 else " stroke-dasharray=\"2.5 2.5\""}/>'
                     for i in range(15))
ART["docker-vm-disk-images-mac"] = svg(
    win(24, 22, 272, 136)
    + _dvm_icon + text(86, 55, "Docker.raw", 15, 600) + text(86, 73, "Disk image", 12, 500, INK2)
    + text(44, 102, "Size", 13, 500, INK2) + text(276, 102, "64 GB", 13, 600, INK2, "end")
    + text(44, 120, "On disk", 13, 600) + text(276, 120, "9 GB", 15, 700, AGE[0], "end")
    + _dvm_pages,
    "Docker.raw reserves 64 GB but uses only 9 GB on disk: two pages filled, the rest only reserved")

# 2026-11-13-old-iphone-backups-mac
# 13 Nov — old iPhone backups: the MobileSync Backup folder as a treemap, one tile per device,
# the old phone's backup big and red, the current phone's small and blue.
def _oib_device(x, y, s, ink, w=11, h=19):
    return (f'<rect x="{x}" y="{y}" width="{w*s}" height="{h*s}" rx="{2.6*s}" fill="none" stroke="{ink}" stroke-width="{1.6*s}" stroke-opacity=".8"/>'
            f'<rect x="{x+(w/2-1.9)*s}" y="{y+2*s}" width="{3.8*s}" height="{1.3*s}" rx="{.65*s}" fill="{ink}" fill-opacity=".8"/>')
ART["old-iphone-backups-mac"] = svg(
    win(24, 18, 272, 144)
    + text(42, 40, "MobileSync", 12, 500, INK2) + text(108, 40, "›", 12, 500, INK3) + text(118, 40, "Backup", 12, 600)
    + treemap(34, 50, 252, 102, [(0, 0, .62, 1, AGE[4]), (.62, 0, .38, .62, AGE[2]), (.62, .62, .38, .38, AGE[0])], 4, 6)
    + _oib_device(48, 64, 1.5, "#1F0806")
    + text(48, 120, "iPhone 11", 14, 600, "#1F0806") + text(48, 138, "64 GB · 4 yrs", 12, 500, "#1F0806", extra='opacity=".85"')
    + _oib_device(198, 60, .85, INK, 15, 19)
    + text(198, 92, "iPad", 12, 600, INK) + text(198, 106, "22 GB · 2 yrs", 11, 500, INK, extra='opacity=".85"')
    + text(198, 130, "iPhone 17", 11, 600, "#0B1D3A") + text(198, 144, "8 GB · today", 10, 500, "#0B1D3A", extra='opacity=".85"'),
    "Phone backups on a Mac: an old iPhone's 64 GB backup, four years untouched, dwarfs the current phone's")

# 2026-11-17-xcode-taking-up-space-mac
# 17 Nov — Xcode taking up space: the Developer folder as a treemap, old device support in red
_xc_tiles = [
    (0, 0, .5, 1, AGE[4]),        # iOS DeviceSupport 63 GB, old builds
    (.5, 0, .5, .62, AGE[0]),     # Simulators 49 GB
    (.5, .62, .3, .38, AGE[3]),   # DerivedData
    (.8, .62, .2, .38, AGE[1]),   # Archives
]
ART["xcode-taking-up-space-mac"] = svg(
    win(24, 16, 272, 148)
    + text(40, 39, "Developer", 14, 600) + text(280, 39, "in your Library", 12, 500, INK2, "end")
    + treemap(34, 48, 252, 108, _xc_tiles)
    + text(46, 70, "iOS DeviceSupport", 12, 600, "#1F0806") + text(46, 86, "63 GB", 12, 500, "#1F0806", extra='opacity=".8"')
    + text(172, 70, "Simulators", 12, 600, "#0B1D3A") + text(172, 86, "49 GB", 12, 500, "#0B1D3A", extra='opacity=".8"')
    + text(169, 133, "DerivedData", 10.5, 600, INK),
    "Xcode's Developer folder as a treemap: old iOS device support files in red, then simulators and DerivedData")

# 2026-11-20-photos-library-taking-space-mac
# 20 Nov — Photos library taking up space: Pictures holds the live library and a forgotten one
def _phl_flower(cx, cy, r, cols):
    out = [f'<rect x="{cx-r-5}" y="{cy-r-5}" width="{2*r+10}" height="{2*r+10}" rx="{(2*r+10)*.24:.1f}" fill="#fff" stroke="#000" stroke-opacity=".1" stroke-width=".75"/>']
    for _k in range(8):
        out.append(f'<ellipse cx="{cx}" cy="{cy - r*.48:.1f}" rx="{r*.26:.1f}" ry="{r*.5:.1f}" fill="{cols[_k % len(cols)]}" fill-opacity=".85" transform="rotate({_k*45} {cx} {cy})"/>')
    return "".join(out)
_phl_rows = [("Photos Library", "55.8 GB", "This month", AGE[0], [AGE[0], AGE[1], AGE[2], AGE[3]], 106),
             ("iPhoto Library", "31.2 GB", "4 years", AGE[4], [AGE[4], AGE[3]], 60)]
_phl = []
for _i, (_n, _gb, _age, _c, _cols, _w) in enumerate(_phl_rows):
    _y = 58 + _i * 50
    if _i == 1:
        _phl.append(f'<rect x="34" y="{_y-6}" width="252" height="46" rx="8" fill="{_c}" fill-opacity=".12"/>')
    _phl.append(_phl_flower(62, _y + 17, 12, _cols) + text(92, _y + 13, _n, 14, 600)
                + bar(92, _y + 22, 106, 7, [(_w, _c)])
                + text(274, _y + 13, _gb, 13, 600, INK, "end")
                + dot(212, _y + 26, _c, 3.5) + text(274, _y + 30, _age, 11, 500, INK2, "end"))
ART["photos-library-taking-space-mac"] = svg(
    win(26, 18, 268, 144)
    + folder(42, 28, .32) + text(66, 41, "Pictures", 13, 600)
    + f'<line x1="26" y1="50" x2="294" y2="50" stroke="#000" stroke-opacity=".07"/>'
    + "".join(_phl),
    "The Pictures folder holding a 55.8 GB Photos library used this month and a forgotten 31.2 GB iPhoto library untouched for four years")

# 2026-11-24-how-much-storage-mac-buy
# 24 Nov — how much storage to buy: today's usage, split active vs dormant, picks a size
_hmsb_opts = []
for _i, (_lab, _sel) in enumerate([("256 GB", False), ("512 GB", True), ("1 TB", False)]):
    _x = 42 + _i * 82
    if _sel:
        _hmsb_opts.append(f'<rect x="{_x}" y="112" width="72" height="30" rx="8" fill="{ACCENT}"/>'
                          + text(_x + 36, 132, _lab, 13, 600, "#fff", "middle"))
    else:
        _hmsb_opts.append(f'<rect x="{_x+.5}" y="112.5" width="71" height="29" rx="8" fill="#fff" stroke="{GREY}" stroke-width="1.2"/>'
                          + text(_x + 36, 132, _lab, 13, 500, INK2, "middle"))
ART["how-much-storage-mac-buy"] = svg(
    win(24, 22, 272, 136)
    + text(42, 48, "Your Mac today", 14, 600) + text(278, 48, "294 GB", 14, 600, INK, "end")
    + bar(42, 60, 236, 12, [(70, AGE[0]), (40, AGE[1]), (24, AGE[2]), (34, AGE[3]), (62, AGE[4])])
    + text(42, 92, "Growing", 11, 600, AGE[0]) + text(278, 92, "Untouched for years", 11, 600, AGE[4], "end")
    + "".join(_hmsb_opts),
    "A Mac's used space split into what is still growing and what is untouched for years, with 512 GB picked from 256 GB, 512 GB and 1 TB")

# 2026-11-27-messages-taking-up-space-mac
# 27 Nov — Messages taking up space: the Messages total over a grid of old attachments, mostly red
_msg_cols = [AGE[4], AGE[4], AGE[3], AGE[4], AGE[0], AGE[4],
             AGE[3], AGE[4], AGE[4], AGE[2], AGE[4], AGE[3]]
_msg_video = {1, 5, 8}
_msg_tiles = []
for _msg_i, _msg_c in enumerate(_msg_cols):
    _msg_x = 44 + (_msg_i % 6) * 39.6
    _msg_y = 72 + (_msg_i // 6) * 40
    _msg_tiles.append(f'<rect x="{_msg_x:.1f}" y="{_msg_y}" width="34" height="34" rx="6" fill="{_msg_c}"/>')
    if _msg_i in _msg_video:
        _msg_tiles.append(f'<path d="M{_msg_x+13:.1f} {_msg_y+10} l10 7 l-10 7Z" fill="#fff" fill-opacity=".92"/>')
    else:
        _msg_tiles.append(f'<path d="M{_msg_x+6:.1f} {_msg_y+27} l8 -9 l6 6 l4 -4 l10 7Z" fill="#fff" fill-opacity=".55"/>'
                          f'<circle cx="{_msg_x+24:.1f}" cy="{_msg_y+10}" r="3" fill="#fff" fill-opacity=".7"/>')
ART["messages-taking-up-space-mac"] = svg(
    win(24, 20, 272, 140)
    + f'<rect x="44" y="36" width="26" height="20" rx="10" fill="{AGE[1]}"/>'
    + f'<path d="M48 52 l-4 8 l9 -5Z" fill="{AGE[1]}"/>'
    + text(80, 52, "Messages", 15, 600)
    + text(276, 52, "38.2 GB", 15, 600, INK, "end")
    + "".join(_msg_tiles),
    "Messages holding 38.2 GB of photo and video attachments, most of them years old")

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

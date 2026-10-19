"""The share bar at the end of every blog post: the system share sheet (iMessage, AirDrop, Mail…),
X, WhatsApp, Reddit, Facebook and Copy link. Plain links, no third-party scripts; /js/share.js
only reveals Share… where the browser supports it and makes Copy link work.
Brand icons: Simple Icons 13.21.0 (CC0)."""
from __future__ import annotations

import html
import urllib.parse

MARK = 'class="share-bar"'
SCRIPT = '<script src="/js/share.js?v=20261019" defer></script>'
ICONS = {'x': 'M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z', 'whatsapp': 'M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z', 'reddit': 'M12 0C5.373 0 0 5.373 0 12c0 3.314 1.343 6.314 3.515 8.485l-2.286 2.286C.775 23.225 1.097 24 1.738 24H12c6.627 0 12-5.373 12-12S18.627 0 12 0Zm4.388 3.199c1.104 0 1.999.895 1.999 1.999 0 1.105-.895 2-1.999 2-.946 0-1.739-.657-1.947-1.539v.002c-1.147.162-2.032 1.15-2.032 2.341v.007c1.776.067 3.4.567 4.686 1.363.473-.363 1.064-.58 1.707-.58 1.547 0 2.802 1.254 2.802 2.802 0 1.117-.655 2.081-1.601 2.531-.088 3.256-3.637 5.876-7.997 5.876-4.361 0-7.905-2.617-7.998-5.87-.954-.447-1.614-1.415-1.614-2.538 0-1.548 1.255-2.802 2.803-2.802.645 0 1.239.218 1.712.585 1.275-.79 2.881-1.291 4.64-1.365v-.01c0-1.663 1.263-3.034 2.88-3.207.188-.911.993-1.595 1.959-1.595Zm-8.085 8.376c-.784 0-1.459.78-1.506 1.797-.047 1.016.64 1.429 1.426 1.429.786 0 1.371-.369 1.418-1.385.047-1.017-.553-1.841-1.338-1.841Zm7.406 0c-.786 0-1.385.824-1.338 1.841.047 1.017.634 1.385 1.418 1.385.785 0 1.473-.413 1.426-1.429-.046-1.017-.721-1.797-1.506-1.797Zm-3.703 4.013c-.974 0-1.907.048-2.77.135-.147.015-.241.168-.183.305.483 1.154 1.622 1.964 2.953 1.964 1.33 0 2.47-.81 2.953-1.964.057-.137-.037-.29-.184-.305-.863-.087-1.795-.135-2.769-.135Z', 'facebook': 'M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z'}
SHARE_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12M7.5 7.5 12 3l4.5 4.5M5 11v8.5A1.5 1.5 0 0 0 6.5 21h11a1.5 1.5 0 0 0 1.5-1.5V11" '
              'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
LINK_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1.2 1.2M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1.2-1.2" '
             'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def _q(s: str) -> str:
    return urllib.parse.quote(s, safe="")


def share_bar(url: str, title: str) -> str:
    """The share bar for one post. url is the canonical URL, title the plain-text headline."""
    a = lambda s: html.escape(s, quote=True)
    brand = lambda k: f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{ICONS[k]}"/></svg>'
    links = [
        ("X", "x", f"https://x.com/intent/post?text={_q(title)}&url={_q(url)}"),
        ("WhatsApp", "whatsapp", f"https://wa.me/?text={_q(title + ' ' + url)}"),
        ("Reddit", "reddit", f"https://www.reddit.com/submit?url={_q(url)}&title={_q(title)}"),
        ("Facebook", "facebook", f"https://www.facebook.com/sharer/sharer.php?u={_q(url)}"),
    ]
    out = [f'<div class="share-bar" data-url="{a(url)}" data-title="{a(title)}">',
           '  <div class="share-inner">',
           '    <p class="share-title" id="share-title">Found this useful? Share it.</p>',
           '    <div class="share-buttons" role="group" aria-labelledby="share-title">',
           f'      <button type="button" class="share-btn share-native" data-share-native hidden>{SHARE_ICON}<span>Share…</span></button>']
    for label, key, href in links:
        out.append(f'      <a class="share-btn" href="{a(href)}" target="_blank" rel="noopener" '
                   f'aria-label="Share on {label} (opens in a new tab)">{brand(key)}<span>{label}</span></a>')
    out += [f'      <button type="button" class="share-btn share-copy" data-share-copy>{LINK_ICON}<span aria-live="polite">Copy link</span></button>',
            '    </div>', '  </div>', '</div>', SCRIPT, '']
    return "\n".join(out)


def add_share_bar(page: str, url: str, title: str) -> str:
    """Insert the share bar before the post's closing call to action (else its related-posts block,
    else the end of <main> or <body>).
    A page that already has one is returned unchanged."""
    if MARK in page:
        return page
    for anchor in ('<div class="article-cta">', '<!-- Related Posts -->', '<div class="related-posts">', '</main>', '</body>'):
        i = page.find(anchor)
        if i != -1:
            line = page.rfind("\n", 0, i) + 1
            return page[:line] + share_bar(url, title) + "\n" + page[line:]
    raise ValueError("no place for the share bar: the page has no article-cta, related-posts, </main> or </body>")

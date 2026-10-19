"""Posting a published article to X: X's weighted length rule and OAuth 1.0a request signing.
Standard library only, so the publish workflow needs nothing installed."""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time
import urllib.parse

X_LIMIT = 280
URL_WEIGHT = 23          # X counts every link as 23 characters (t.co)
TEXT_LIMIT = X_LIMIT - 1 - URL_WEIGHT   # the article link is appended after one space
# twitter-text v3: these code point ranges weigh 1, everything else (CJK, emoji, …) weighs 2
_LIGHT = ((0, 4351), (8192, 8205), (8208, 8223), (8242, 8247))


def weighted_length(text: str) -> int:
    return sum(1 if any(a <= ord(ch) <= b for a, b in _LIGHT) else 2 for ch in text)


def check_x_post(value) -> list[str]:
    """Problems with a package's x_post text (the article URL is added when posting)."""
    if value is None:
        return []
    if not isinstance(value, str) or not value.strip():
        return ["x_post must be non-empty text, or left out"]
    errs = []
    if "http://" in value or "https://" in value:
        errs.append("x_post must not contain a link: the article URL is added automatically")
    n = weighted_length(value)
    if n > TEXT_LIMIT:
        errs.append(f"x_post is {n} characters by X's count; the limit is {TEXT_LIMIT} (280 minus the link)")
    return errs


def _enc(s: str) -> str:
    return urllib.parse.quote(str(s), safe="~-._")


def oauth_signature(method: str, url: str, params: dict, consumer_secret: str, token_secret: str) -> str:
    """HMAC-SHA1 OAuth 1.0a signature over the method, URL and all oauth/query/form params."""
    pairs = sorted((_enc(k), _enc(v)) for k, v in params.items())
    base = "&".join([method.upper(), _enc(url), _enc("&".join(f"{k}={v}" for k, v in pairs))])
    key = f"{_enc(consumer_secret)}&{_enc(token_secret)}"
    return base64.b64encode(hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()


def oauth_header(method: str, url: str, consumer_key: str, consumer_secret: str,
                 token: str, token_secret: str, nonce: str | None = None, timestamp: str | None = None) -> str:
    """Authorization header for a request whose body is JSON (so the body is not signed)."""
    oauth = {"oauth_consumer_key": consumer_key, "oauth_nonce": nonce or secrets.token_hex(16),
             "oauth_signature_method": "HMAC-SHA1", "oauth_timestamp": timestamp or str(int(time.time())),
             "oauth_token": token, "oauth_version": "1.0"}
    oauth["oauth_signature"] = oauth_signature(method, url, oauth, consumer_secret, token_secret)
    return "OAuth " + ", ".join(f'{_enc(k)}="{_enc(v)}"' for k, v in sorted(oauth.items()))

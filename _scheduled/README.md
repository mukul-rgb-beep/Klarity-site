# Queued blog posts

Each folder here is one approved post waiting for its date: `YYYY-MM-DD-<slug>/` with
`package.json`, `post.html`, `card.html` and optional `assets/`. This folder is not deployed
(`.assetsignore`), so drafts are readable on GitHub but 404 on www.klaritydisk.com.

The "Publish scheduled posts" workflow runs daily at 09:00 IST and publishes anything due.
Validate locally before pushing: `python3 .github/scripts/publish.py check`.
Preview a publish: `python3 .github/scripts/publish.py publish --date YYYY-MM-DD --dry-run`.
Design: Klarity repo, docs/superpowers/specs/2026-09-29-scheduled-blog-publishing-design.md.

Optional in package.json: `"x_post": "text"`, the post for X, approved with the article. The link is
added automatically, so leave it out of the text (limit 256 by X's count). On publish day the
"Published" issue carries a one-click Share on X link with this text (or the headline). If the
X_API_KEY / X_API_SECRET / X_ACCESS_TOKEN / X_ACCESS_SECRET secrets are ever set, the workflow
posts it through the X API instead (pay-per-use). Every post also gets the reader share bar
(blogpub/share.py) when it is published.

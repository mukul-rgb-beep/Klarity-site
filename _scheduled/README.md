# Queued blog posts

Each folder here is one approved post waiting for its date: `YYYY-MM-DD-<slug>/` with
`package.json`, `post.html`, `card.html` and optional `assets/`. This folder is not deployed
(`.assetsignore`), so drafts are readable on GitHub but 404 on www.klaritydisk.com.

The "Publish scheduled posts" workflow runs daily at 09:00 IST and publishes anything due.
Validate locally before pushing: `python3 .github/scripts/publish.py check`.
Preview a publish: `python3 .github/scripts/publish.py publish --date YYYY-MM-DD --dry-run`.
Design: Klarity repo, docs/superpowers/specs/2026-09-29-scheduled-blog-publishing-design.md.

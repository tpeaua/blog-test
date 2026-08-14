#!/usr/bin/env python3
"""Tiny, dependency-free static site generator.

Reads Markdown posts from site/posts/, renders them with site/layout.html into
dist/. Deterministic: same inputs -> byte-identical output (no clock, no RNG).
"""
import re
import sys
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DIST = ROOT / "dist"
POSTS = SITE / "posts"

SITE_TITLE = "My Blog"
TAGLINE = "A few posts, nothing fancy."


def parse_front_matter(text: str):
    """Split a post into (meta, body). Front matter is YAML-ish key: value lines."""
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = parts[2]
    return meta, body.strip()


def inline_md(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def render_block(block: str) -> str:
    lines = block.splitlines()
    out = []

    if lines and lines[0].startswith("```"):
        lang = lines[0][3:].strip()
        code = "\n".join(lines[1:-1]) if lines[-1].startswith("```") else "\n".join(lines[1:])
        return f'<pre><code class="language-{lang}">{html.escape(code)}</code></pre>'

    for line in lines:
        if not line.strip():
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", line)
        if h:
            level = len(h.group(1))
            out.append(f"<h{level}>{inline_md(h.group(2))}</h{level}>")
            continue
        if re.match(r"^(\*{3,}|-{3,}|_{3,})$", line.strip()):
            out.append("<hr />")
            continue
        q = re.match(r"^>\s?(.*)$", line)
        if q:
            out.append(f"<blockquote>{inline_md(q.group(1))}</blockquote>")
            continue
        li = re.match(r"^\s*[-*+]\s+(.*)$", line)
        if li:
            out.append(f"<li>{inline_md(li.group(1))}</li>")
            continue
        nli = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if nli:
            out.append(f"<li>{inline_md(nli.group(1))}</li>")
            continue
        out.append(f"<p>{inline_md(line)}</p>")

    # crude list wrapping: consecutive <li> get wrapped in <ul> (unordered only)
    result = []
    buf = []
    for part in out:
        if part.startswith("<li>"):
            buf.append(part)
        else:
            if buf:
                result.append("<ul>" + "".join(buf) + "</ul>")
                buf = []
            result.append(part)
    if buf:
        result.append("<ul>" + "".join(buf) + "</ul>")
    return "\n".join(result)


def markdown_to_html(md: str) -> str:
    # split into blocks on blank lines, but keep fenced code blocks intact
    blocks = []
    cur = []
    in_fence = False
    for line in md.splitlines():
        if line.startswith("```"):
            if in_fence:
                cur.append(line)
                blocks.append("\n".join(cur))
                cur = []
                in_fence = False
            else:
                if cur:
                    blocks.append("\n".join(cur))
                    cur = []
                cur.append(line)
                in_fence = True
        else:
            cur.append(line)
    if cur:
        blocks.append("\n".join(cur))
    return "\n".join(render_block(b) for b in blocks if b.strip())


def slug_from_filename(name: str) -> str:
    return Path(name).stem


def plain_text(md: str) -> str:
    """Strip basic markdown markers for a plain-text excerpt."""
    t = re.sub(r"`([^`]+)`", r"\1", md)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*", r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    return t


def main() -> int:
    layout = (SITE / "layout.html").read_text()
    about = (SITE / "about.html").read_text()

    posts = []
    for path in sorted(POSTS.glob("*.md")):
        meta, body = parse_front_matter(path.read_text())
        slug = slug_from_filename(path.name)
        posts.append({
            "slug": slug,
            "title": meta.get("title", slug.replace("-", " ").title()),
            "date": meta.get("date", ""),
            "tags": [t for t in meta.get("tags", "").strip("[]").split(",") if t.strip()],
            "body": markdown_to_html(body),
            "excerpt": plain_text(body.split("\n\n")[0][:220]).strip(),
        })

    posts.sort(key=lambda p: p["date"], reverse=True)

    if DIST.exists():
        import shutil
        shutil.rmtree(DIST)
    (DIST / "posts").mkdir(parents=True)
    (DIST / "assets").mkdir(parents=True)

    # index
    items = []
    for p in posts:
        tags = " ".join(f'<span>{t.strip()}</span>' for t in p["tags"])
        items.append(
            f'<li><a class="title" href="posts/{p["slug"]}.html">{html.escape(p["title"])}</a>'
            f'<div class="date">{html.escape(p["date"])} &middot; <span class="tags">{tags}</span></div>'
            f'<p class="excerpt">{html.escape(p["excerpt"])}</p></li>'
        )
    index_html = layout.replace("{{TITLE}}", SITE_TITLE).replace(
        "{{ROOT}}", ""
    ).replace("{{SITE_TITLE}}", SITE_TITLE).replace(
        "{{TAGLINE}}", TAGLINE
    ).replace(
        "{{CONTENT}}", f'<h2>Posts</h2><ul class="post-list">{"".join(items)}</ul>'
    ).replace("{{YEAR}}", "2026")
    (DIST / "index.html").write_text(index_html)

    # about
    about_html = about.replace("{{ROOT}}", "").replace("{{SITE_TITLE}}", SITE_TITLE).replace(
        "{{TAGLINE}}", TAGLINE
    ).replace("{{YEAR}}", "2026")
    (DIST / "about.html").write_text(about_html)

    # posts
    for p in posts:
        meta = f'<div class="meta">{html.escape(p["date"])} &middot; <span class="tags">{" ".join(f"<span>{html.escape(t.strip())}</span>" for t in p["tags"])}</span></div>'
        content = f'<article class="post"><h1>{html.escape(p["title"])}</h1>{meta}{p["body"]}</article>'
        page = layout.replace("{{TITLE}}", f'{p["title"]} — {SITE_TITLE}').replace(
            "{{ROOT}}", "../"
        ).replace("{{SITE_TITLE}}", SITE_TITLE).replace(
            "{{TAGLINE}}", TAGLINE
        ).replace("{{CONTENT}}", content).replace("{{YEAR}}", "2026")
        (DIST / "posts" / f'{p["slug"]}.html').write_text(page)

    # assets
    import shutil
    shutil.copy2(SITE / "assets" / "style.css", DIST / "assets" / "style.css")

    print(f"built {len(posts)} post(s) -> {DIST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

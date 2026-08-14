---
title: Hello, world
date: 2026-08-14
tags: [intro, meta]
---

Welcome to the first post on this blog. This site is deliberately small: posts are
plain Markdown files, and a tiny build script turns them into static HTML.

The interesting part is what runs *behind* the site — an **agentic team** built on
[Meridian](https://github.com/Cambrionic/meridian). The team looks like this:

- **Writer** — drafts a post from a one-line brief.
- **Editor** — tightens the draft: clarity, tone, structure.
- **Reviewer** — gates it: approve, or send it back for revision.
- **Publisher** — writes the post into the site and rebuilds it.

Every step is an effect, and every effect is journaled. That means the whole run can
be **replayed byte-for-byte at $0** — no model calls, no cost, just the recorded
inputs played back. That's the promise of reproducible agent workflows.

Stick around. The next few posts go deeper into how the team works.

# AGENTS.md

This directory is the **blog-test** project: a static blog whose content is produced by
an agentic team running on Meridian.

- **Site source** lives in `site/` — posts are Markdown in `site/posts/` with front
  matter (`title`, `date`, `tags`). Rebuild with `python3 scripts/build.py` (writes `dist/`).
- **The team is data**: `.meridian/team/content-team.json` (writer → editor → reviewer →
  gate → publish → build) and `.meridian/team/content-fanout.json` (parallel pitch).
- **Deploy**: `.meridian/deploy/deploy.json` + `scripts/deploy.sh`.
- **Add a post**: `scripts/new-post.sh "Topic" [slug] [tone]`.

Meridian verbs: `meridian validate <spec>`, `meridian plan <spec>`, `meridian run <spec>
--allow ... --input seed.json`, `meridian replay run.jsonl`. `llm` effects need the
`claude` CLI on PATH; deterministic legs (`fs.write`, `bash.run`, deploy) need nothing.

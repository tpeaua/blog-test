# blog-test

A tiny, dependency-free static blog whose content is produced by an **agentic team**
running on [Meridian](https://github.com/Cambrionic/meridian) (workflows-as-data,
byte-identical `$0` replay).

## Layout

```
site/               # the site source (Markdown posts, layout, css)
  posts/*.md        # one Markdown file per post (front matter: title/date/tags)
  layout.html       # shared page shell
  assets/style.css
scripts/
  build.py          # Markdown -> static HTML into dist/ (dependency-free, deterministic)
  deploy.sh         # build; push dist/ to GitHub Pages when DEPLOY_REMOTE is set
  new-post.sh       # seed a Brief + run the content team
.meridian/
  team/content-team.json   # the agentic team: writer -> editor -> reviewer -> gate -> publish -> build
  team/content-fanout.json # parallel pitch team: N writers, pick the best draft
  deploy/deploy.json       # build + smoke-check + ship (deterministic, $0)
dist/               # generated static site (gitignored)
```

## The agentic team

The team is **data**, not code — a `DomainSpec` JSON with components (schemas) and
steps (what fires, in what order). Roles:

| Role | Step | Effect |
| --- | --- | --- |
| Writer | `writer` | `llm` — draft from a `team.Brief` |
| Editor | `editor` | `llm` — tighten the draft |
| Reviewer | `reviewer` | `llm` — approve or revise |
| Gate | `gate` | `conditional` — route approve → publish, revise → done |
| Publisher | `publish` + `build` | `fs.write` + `bash.run` — write the post, rebuild the site |

Every effect is journaled, so a run can be **replayed byte-for-byte at `$0`**.

## Commands

```sh
# validate / preview (offline, $0)
meridian validate .meridian/team/content-team.json
meridian plan     .meridian/team/content-team.json

# build the site now (deterministic, no model needed)
python3 scripts/build.py            # -> dist/

# deploy (deterministic, $0; push requires DEPLOY_REMOTE + a git remote)
DEPLOY_REMOTE=origin scripts/deploy.sh

# deploy through Meridian (journaled + replayable)
meridian run .meridian/deploy/deploy.json --allow bash.run \
      --input .meridian/deploy/seed.json --out .meridian/deploy/run.jsonl
meridian replay .meridian/deploy/run.jsonl

# add a post through the agentic team (uses the `pi` provider by default)
scripts/new-post.sh "Your topic" my-slug conversational

# ...or run the team directly
meridian run .meridian/team/content-team.json --provider pi \
      --allow llm,fs.write,bash.run --input .meridian/team/seed-example.json \
      --out .meridian/team/run.jsonl
meridian replay .meridian/team/run.jsonl
```

## Live-leg note

The `llm` effects (writer/editor/reviewer) need a live provider. Meridian defaults to
the **`claude` CLI**; this project uses the **`pi`** CLI via `--provider pi` (added in a
small local patch to `engine/cmd/meridian/run.go`). `fs.write`, `bash.run`, the deploy
workflow, and every replay are `$0` and need nothing external.

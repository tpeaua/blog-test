---
title: The team is data
date: 2026-08-15
tags: [meridian, workflows]
---

Most "agent teams" are hand-rolled: a prompt here, a loop there, some glue code, and
a lot of vibes. This blog's team is different — it's **data**.

The team is declared as a `DomainSpec`: a JSON document that names components
(schemas) and steps (what fires, in what order). The engine drives the steps to
quiescence. No hand-written systems, no framework code.

## A step, in the raw

```json
{
  "kind": "emit-effect",
  "name": "writer",
  "when": ["team.Brief"],
  "effect": "llm",
  "prompt": "You are the writer. Draft a post for: {{team.Brief.topic}}",
  "resultCid": "team.Draft"
}
```

That one step says: when a `team.Brief` component exists, fire an `llm` effect with
this prompt, and store the result as `team.Draft`. The `{{team.Brief.topic}}` is
template interpolation — data shaping stays out of the language.

## Why this wins

- **Hot-loading** — change the workflow JSON and re-run; no restart.
- **Replay** — the run is journaled, so you can re-run it for $0, byte-identical.
- **Reviewability** — the team is a document a human (or another agent) can read.

The team that builds this site is four roles wired together as data. The next post
walks through the full pipeline.

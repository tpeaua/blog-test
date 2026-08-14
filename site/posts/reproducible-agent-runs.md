---
title: Why reproducible agent runs matter
date: 2026-08-15
tags: [agents, reproducibility]
---

Running an agent costs money and is non-deterministic. Run the same prompt twice and
you get two different answers — usually both fine, sometimes not, and you can't tell
which one you shipped last week.

Reproducibility flips that. The idea behind
[Meridian](https://github.com/Cambrionic/meridian) is simple and specific:

1. **Record** every non-deterministic input an agent touches — model output, shell
   result, file read — as it happens.
2. **Replay** the run later against that record.

The replay is **byte-identical**, makes **zero live model calls**, and costs **$0**.

What this is *not*: it does not make the model itself deterministic. A live run can
still answer differently every time. What it makes deterministic is the *replay of
what already happened* — which turns out to be the part you actually need when you're
debugging, diffing prompt versions, or proving what changed.

## Why it changes your workflow

- **Diff two prompt versions** on the same inputs without re-paying for the model.
- **Catch a regression** before it ships by replaying the recorded run.
- **Step through a flaky run** deterministically instead of re-running it live.

The workflow itself is data — a JSON document — so an agent can author, extend, and
hot-load it, then cheaply replay to check its own change.

That's the whole trick. Cheap iteration on expensive, noisy processes.

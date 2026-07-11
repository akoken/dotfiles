---
name: graphify
description: Build or query a persistent knowledge graph for broad architecture, cross-file relationships, or mixed code-and-document corpora. Use when the user explicitly asks for Graphify or a knowledge graph, when graphify-out already exists and can answer an architecture question, or when persistent cross-session mapping materially helps. Do not trigger for routine code questions, focused audits, or small repository tasks.
---

# Graphify

Choose exactly one branch.

## Existing Graph

If `graphify-out/graph.json` exists and the user asks a natural-language architecture or relationship question, use the query branch before broad source browsing.

- Query: locate `## For /graphify query` in [references/full-workflow.md](references/full-workflow.md).
- Shortest path: locate `## For /graphify path`.
- Explain a node: locate `## For /graphify explain`.

Answer only from graph output and cited source locations. If the graph is insufficient or stale, say so and inspect the smallest necessary source scope.

## Build or Update

Run a build only when the user explicitly requests Graphify/a knowledge graph or persistent mapping clearly justifies extraction cost.

1. Resolve the narrowest user-named scope; do not silently expand to the repository root.
2. For a single target, change into its resolved root before running the pipeline so `graphify-out/` stays inside that scope.
3. Read `## What You Must Do When Invoked` through `## For --update` in [references/full-workflow.md](references/full-workflow.md).
4. Run detection before semantic extraction and obey the corpus-size guardrail.
5. For an existing graph with changed files, use the update branch rather than rebuilding everything.
6. Complete the workflow's manifest, cost, cleanup, and output checks before reporting success.

For `/graphify --help` or `-h`, read and print the reference's `## Usage` section verbatim and stop.

## Other Explicit Branches

Use `rg -n '^## For |^### Step' references/full-workflow.md` to locate:

- cluster-only;
- add URL;
- watch mode;
- commit hook;
- native agent-instruction integration;
- optional exports such as SVG, GraphML, Neo4j, MCP, HTML, or Obsidian.

## Honesty and Cost

- Never invent graph edges or source locations.
- Preserve EXTRACTED, INFERRED, and AMBIGUOUS distinctions.
- Never skip the corpus warning or hide token cost.
- Do not generate expensive visualization or semantic extraction when the selected branch does not need it.
- Treat the graph as an index, not stronger evidence than the underlying source.

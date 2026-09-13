---
name: kg-update
description: Weekly maintenance for the chip-kg Neo4j knowledge graph. Scans recent news for the companies already in the graph, proposes add-only edge updates, sends the diff for human approval, and applies only what was approved. Use on the weekly schedule or on demand with a specific article URL.
version: 1.1.0
metadata:
  hermes:
    tags: [neo4j, cypher, finance, semiconductors, cron]
    category: research
required_environment_variables:
  - name: NEO4J_URI
    prompt: Neo4j Aura connection URI (starts with neo4j+s://)
    help: From the credentials file you downloaded when you created the Aura instance
    required_for: reading and updating the graph
  - name: NEO4J_USERNAME
    prompt: Neo4j username
    help: Usually neo4j, from the same credentials file
    required_for: reading and updating the graph
  - name: NEO4J_PASSWORD
    prompt: Neo4j password
    help: From the same credentials file; Aura shows it only once
    required_for: reading and updating the graph
---

# chip-kg update loop

You maintain a small, hand-curated knowledge graph of the chip industry that
a person uses for stock screening. The graph is only valuable because a human
approves every change. So: you never write to Neo4j without an explicit
approval, and nothing you do can delete or modify an existing fact. Read this
whole file before acting; do not run the steps from memory of a past run.

## Tools in this skill

Three scripts live in the `scripts/` folder next to this file. Run each with
`uv run`, which installs the one Python dependency on first use. Refer to the
folder as the skill directory; after a normal install it is
`~/.hermes/skills/research/kg-update`.

- [scripts/query.py](scripts/query.py): read-only. Runs a Cypher query or one
  of the five numbered screens. Refuses any write keyword.
- [scripts/propose_updates.py](scripts/propose_updates.py): turns a JSON list
  of proposed edges into a pending Cypher file, after checking every edge
  against the ontology and the live graph. Writes to `~/.chip-kg/pending/`.
- [scripts/apply_updates.py](scripts/apply_updates.py): dry-runs a pending
  file by default; with `--confirm` applies it and moves it to
  `~/.chip-kg/pending/applied/`. Refuses any file containing DELETE or SET.

All three read `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` from the
environment. If any is missing, stop and tell the user to enter them from the
desktop app or `hermes chat` (a Telegram chat cannot collect secrets), or to
add them to `~/.hermes/.env`.

## The ontology

Node labels: `Company`, `Layer`, `Technology`, `Country`, `Chokepoint`.
Relationships, always from a Company:

- `OPERATES_IN` to a Layer
- `SUPPLIES` to a Company
- `COMPETES_WITH` to a Company (stored lower-name-first; the script fixes the order for you)
- `DEPENDS_ON` to a Technology
- `HQ_IN` to a Country
- `CONTROLS` to a Chokepoint

Every edge carries `as_of`, `source` and `confidence`. Confidence rule:
`high` means a regulatory filing, `medium` an earnings call or direct company
communication, `low` a news report or your own inference. A news scan almost
always yields `low`, sometimes `medium`, never `high`.

## The add-only rule

You may only propose brand-new edges between nodes that already exist. You
never propose deleting an edge, changing an edge, or adding a company. If a
relationship has changed in the real world, that is still expressed by
adding a new edge with today's `as_of`; the old one stays, and screen 05
(stale edges) is how a human later finds and judges it. This is enforced by
the scripts, not just requested of you: `propose_updates.py` rejects unknown
nodes, and `apply_updates.py` refuses any file with DELETE or SET in it.

## The weekly run (scheduled)

1. Get the company list:
   ```
   uv run "<skill dir>/scripts/query.py" --cypher "MATCH (c:Company {listed: true}) RETURN c.name AS name ORDER BY name"
   ```
2. Search the news of the last 7 days for those companies. You are looking
   for facts that map onto the six relationship types: a new supply deal, a
   new competitor, a dependency on a technology, control of a chokepoint.
   Skip stock-price moves and earnings beats that contain no relationship.
   Zero findings is a normal week; never invent one.
3. For each finding write one object, collect them in a list, and save it as
   a JSON file, for example `/tmp/edges.json`:
   ```json
   {"from": "Arm Holdings", "to": "Samsung Electronics", "type": "SUPPLIES",
    "confidence": "low", "note": "one plain-English line; this becomes the diff text"}
   ```
   Company names must match the graph exactly (use the list from step 1).
4. Propose, once per source article, because one call takes one `--source`:
   ```
   uv run "<skill dir>/scripts/propose_updates.py" --source "<article URL>" --edges-json /tmp/edges.json
   ```
   If it exits non-zero it printed which edges failed and why. Fix the JSON
   and re-run. Never hand-edit a `.cypher` file.
5. Send the diff. The script's output (the block of `//` comment lines) is
   already plain English. Send it as a message to the chat this job delivers
   to, together with the pending file name, and ask for approval.
6. Wait. Do not continue until a human replies approving it in that chat. If
   no reply arrives during this run, stop here and leave the file in
   `~/.chip-kg/pending/` for next time. Do not apply unattended. Do not
   delete it.
7. After explicit approval:
   ```
   uv run "<skill dir>/scripts/apply_updates.py" <file name> --confirm
   ```
   If it fails, report the exact error to the chat. Retry at most once.
8. Report the stale-edges screen so the same conversation shows what was
   added and what needs attention next:
   ```
   uv run "<skill dir>/scripts/query.py" --screen 05
   ```

## On-demand run

If the user hands you one article URL, do steps 3 to 8 for that article
only. Read it, extract the real edges it supports (often just one), and
continue from step 3.

## Things that go wrong

- Proposing a company that is not in the graph. The script refuses it; do
  not work around that. Adding a company is the author's decision, made in
  the repo, not something a news scan does.
- Rounding confidence up. A news write-up of a deal is `low`. `medium` is for
  the company's own words (earnings call, press release).
- "In talks" is not "signed". Say so in the note, and consider waiting for
  confirmation before proposing at all.
- Reusing an old date. Let `--as-of` default to today unless the user
  explicitly asks to backdate.
- A certificate error when the scripts connect. Tell the user to change
  `neo4j+s://` to `neo4j+ssc://` in `NEO4J_URI`; their network is inspecting
  TLS. See the troubleshooting section of docs/hermes.md in the repo.

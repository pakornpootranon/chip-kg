---
name: kg-update
description: Scan recent news for the chip-kg company list and propose add-only edge updates for human approval before writing to Neo4j. Use on the weekly schedule, or on demand when the author names a specific news item.
version: 1.0.0
metadata:
  hermes:
    tags: [neo4j, cypher, finance, cron]
    category: research
    config:
      - key: chip_kg.repo_path
        description: "Local path to the chip-kg repo checkout"
        prompt: "Where is the chip-kg repo checked out on this machine?"
required_environment_variables:
  - name: NEO4J_URI
    prompt: Neo4j Aura connection URI (neo4j+s://...)
    help: From the Aura console for this graph's instance
    required_for: applying approved updates
  - name: NEO4J_USER
    prompt: Neo4j username
    help: Usually "neo4j"
    required_for: applying approved updates
  - name: NEO4J_PASSWORD
    prompt: Neo4j password
    help: From the Aura console; shown only once when the instance was created
    required_for: applying approved updates
---

# chip-kg update loop

You are proposing changes to a small, hand-curated chip-industry knowledge
graph. The whole value of this graph is that a human reviews every change
before it lands — you never write to Neo4j without approval, and you never
delete or modify an existing fact. Read this whole file before doing
anything; do not start executing the steps below from memory of a past run.

## The ontology (so you don't invent something that doesn't fit)

Node labels: `Company`, `Layer`, `Technology`, `Country`, `Chokepoint`.
Relationship types, always `(Company)-[TYPE]->(?)`:

- `OPERATES_IN` -> Layer
- `SUPPLIES` -> Company
- `COMPETES_WITH` -> Company (written lower-name-first; the script fixes this for you if you get it backwards)
- `DEPENDS_ON` -> Technology
- `HQ_IN` -> Country
- `CONTROLS` -> Chokepoint

Every edge carries `as_of`, `source`, `confidence` (`high` = filing, `medium`
= earnings call or company communication, `low` = news or inference — most
of what you propose from a news scan will be `low` or `medium`, essentially
never `high`).

**The add-only rule, stated plainly:** you may only propose brand-new edges.
You never propose deleting an edge, and you never propose changing the
properties of an edge that already exists. If a company relationship has
changed (e.g. a competitor exited a market), that's still expressed by
adding a *new* edge with today's `as_of` — the old one stays, and a human
reading `cypher/screens/05_stale_edges.cypher` later is how staleness gets
surfaced and judged, not an automatic overwrite. This isn't just a
convention: `scripts/apply_updates.py` will refuse to run any file that
contains the words DELETE or SET outside a comment, so there's a technical
backstop if you (or your extraction) ever try to violate it.

## Company list

Only propose edges between companies (or Chokepoints/Technologies/
Countries/Layers) that already exist in the graph. `propose_updates.py`
validates this and will reject anything else with a clear error rather than
silently creating a new node — this skill adds edges, never nodes. To get
the current company list, read `data/nodes.csv` in the repo, or query the
graph directly:

```cypher
MATCH (c:Company {listed: true}) RETURN c.name ORDER BY c.name
```

## The weekly run (scheduled)

1. **Read the company list** (query above).
2. **Search for recent news** on those companies from the last 7 days
   (or whatever window this run covers) — supply deals, competitive moves,
   capacity/technology dependencies, chokepoint changes. You're looking for
   facts that map cleanly onto the six relationship types above; skip
   anything that's just a stock-price move or a generic earnings beat with
   no new relationship in it.
3. **For each real finding**, write one JSON object:
   ```json
   {"from": "Arm Holdings", "to": "Samsung Electronics", "type": "SUPPLIES",
    "confidence": "low", "note": "one-line plain-English reason, becomes the diff text"}
   ```
   Collect them into a list and save as a temp file, e.g. `/tmp/edges.json`.
   Be conservative — a smaller number of well-sourced edges beats padding
   the list. Zero findings in a given week is a fine, normal outcome; don't
   invent a finding to have something to report.
4. **Run the propose script**, once per distinct source URL (each run's
   `source` applies to every edge in that call, so don't mix edges from two
   different articles into one call):
   ```bash
   cd <chip_kg.repo_path>
   python scripts/propose_updates.py --source "<news URL>" --edges-json /tmp/edges.json
   ```
   If it exits non-zero, it printed exactly which edges failed and why —
   fix your JSON (usually a company-name typo or wrong edge direction) and
   re-run. Don't hand-edit a `.cypher` file to work around a validation
   failure.
5. **Send the diff to Telegram.** The script's stdout output (or the header
   comment block of the `pending/<date>.cypher` file it wrote) is already a
   plain-English diff — send that text as a message to the chat this cron
   job was created in. Include the pending filename so a human can refer to
   it by name.
6. **Wait for approval.** Do not proceed to step 7 until a human replies
   approving the change in that same chat. If nobody replies within this
   run, stop here — leave the file in `pending/` for the next run (or a
   manual review) to pick up; do not apply it unattended, and do not delete
   it.
7. **Apply, only after explicit approval:**
   ```bash
   python scripts/apply_updates.py pending/<date>.cypher --confirm
   ```
   This moves the file to `pending/applied/` on success. If it fails, report
   the exact error back to the chat — don't retry silently more than once.
8. **Re-run the stale-edges screen and report the result** to the chat, so
   the same conversation shows both what was just added and the current
   state of anything that needs a human's attention next:
   ```cypher
   :param months => 6;
   MATCH (a)-[r]->(b) WHERE date(r.as_of) < date() - duration({months: $months})
   RETURN type(r) AS relationship, a.name AS from_company, b.name AS to_node,
          r.as_of AS as_of, r.source AS source, r.confidence AS confidence
   ORDER BY r.as_of ASC;
   ```

## On-demand run

The author may instead just hand you a single news URL or link and ask you
to propose an update from it. Same steps 3-8 above, minus the broad search
in step 2 — read the one article, extract whatever real edges it supports
(often just one), and continue from step 3.

## Things that have gone wrong before, watch for these

- Don't propose an edge for a company that isn't in the graph yet — that's
  out of scope for this skill (adding a *node* is a bigger decision the
  author makes deliberately, not something a weekly news scan should do).
- Don't reuse an old `pending/*.cypher` file's `as_of` — always let the
  script default to today's date unless the author explicitly backdates it.
- Confidence is `low` far more often than not for a news-sourced edge.
  Resist the pull to round up to `medium` just because a story sounds
  authoritative — `medium` is for an earnings call or direct company
  communication, not a news write-up of one.
- If a headline is about a company *considering* or *in talks for* a deal,
  that is weaker than an announced/signed one — say so in the `note`, and
  consider whether it's worth proposing yet at all versus waiting for
  confirmation.

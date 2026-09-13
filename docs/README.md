# chip-kg

A small knowledge graph of the semiconductor industry — companies, supply chain
layers, technologies, countries, and chokepoints — built for relationship-based
stock screening. Query it by hand in Neo4j Browser, through Claude via MCP, or
through a scheduled Hermes Agent job.

No engineering background required. Follow these steps in order.

## 1. Create a free Neo4j AuraDB instance

1. Go to [console.neo4j.io](https://console.neo4j.io) and sign up (free tier).
2. Create a new **AuraDB Free** instance.
3. Download the credentials file it gives you (`NEO4J_URI`, `NEO4J_USERNAME`,
   `NEO4J_PASSWORD`). Keep it safe — the password is shown only once.
4. Wait a minute or two for the instance to finish starting (status "Running"
   in the console).

## 2. Load the graph

Open the Neo4j Browser for your instance (link in the Aura console) and paste
in the contents of [`cypher/load.cypher`](../cypher/load.cypher). It creates
the constraints, then loads every company, layer, technology, country, and
chokepoint, then all the relationships between them — straight from this
repo's CSVs on GitHub. Re-running it is safe.

## 3. Run your first screen

Still in Neo4j Browser, paste in
[`cypher/screens/01_single_source_chokepoints.cypher`](../cypher/screens/01_single_source_chokepoints.cypher).
It lists every chokepoint in the chip supply chain controlled by exactly one
company — the highest-conviction picks-and-shovels names. See
[`docs/screens.md`](screens.md) for what each screen finds and why it matters.

## 4. Ask Claude questions about the graph

See [`docs/mcp.md`](mcp.md) for how to connect Claude (Desktop or Code) to
your Aura instance and ask it questions in plain English.

## 5. Keep it updated automatically (optional)

The graph stays useful only if someone keeps adding real news to it. Rather
than doing that by hand forever, [`skills/kg-update/SKILL.md`](../skills/kg-update/SKILL.md)
is a Hermes Agent skill: it scans recent news for the companies already in
the graph, proposes new edges (never deletions, never edits to an existing
edge — see `CLAUDE.md`'s data rules), sends you the diff, and only writes to
Neo4j after you approve it.

**Setup** (needs a free [Hermes Agent](https://hermes-agent.nousresearch.com)
account):

1. Install the skill: point Hermes at `skills/kg-update/SKILL.md` in this
   repo (or copy its contents into a new skill in the Hermes UI).
2. When prompted, give it `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` — the
   same credentials from step 1 above.
3. Create the weekly cron job:
   ```
   hermes cron create "every monday 07:00" "Run the kg-update skill: scan news for the current chip-kg company list from the past 7 days, propose edges, send the diff, wait for approval, apply, re-run the stale-edges screen" --skill kg-update
   ```
   **Timezone note:** Hermes schedules "every monday 07:00" against your
   Hermes instance's local clock, not a named timezone — there's no
   `Asia/Bangkok` field to set. If your Hermes instance doesn't already run
   on Bangkok time, either adjust the hour you pass here to match, or check
   your instance's timezone setting before creating the job.
4. Company list: the skill queries `MATCH (c:Company {listed: true}) RETURN
   c.name` itself each run, so you never need to hand it a static list —
   newly added companies (from a future `data/nodes.csv` update) are picked
   up automatically on the next run.
5. The first time it finds something, it'll message you in whatever chat
   you created the cron job from (Telegram, if that's how your Hermes
   instance is connected — see [`docs/telegram.md`](telegram.md) once that
   exists). Reply to approve before it writes anything.

**Fallback: no Hermes, plain cron.** The two scripts underneath the skill
have no Hermes-specific dependency — they're plain Python (`neo4j` package
only) and can run from any machine's cron:

```cron
0 0 * * 1 cd /path/to/chip-kg && python scripts/propose_updates.py --source "$NEWS_URL" --edges-json /path/to/edges.json && mail -s "chip-kg pending update" you@example.com < pending/$(date +\%F).cypher
```

You'd still need something to decide `$NEWS_URL` and write `edges.json` —
without an LLM agent doing that step, this fallback only really works for a
person who already has a specific article in mind and wants the mechanical
validation/formatting handled for them, run manually rather than on a
schedule:

```bash
python scripts/propose_updates.py --source "https://..." --edges-json edges.json
# review pending/<date>.cypher, then:
NEO4J_URI=... NEO4J_USER=... NEO4J_PASSWORD=... python scripts/apply_updates.py pending/<date>.cypher --confirm
```

## What's in this repo

See [`../CLAUDE.md`](../CLAUDE.md) for the full ontology and data rules.

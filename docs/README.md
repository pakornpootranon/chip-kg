# chip-kg

A small knowledge graph of the semiconductor industry (companies, supply chain
layers, technologies, countries, and chokepoints) built for relationship-based
stock screening. Query it by hand in Neo4j Browser, through Claude via MCP, or
through a scheduled Hermes Agent job.

No engineering background required. Follow these steps in order.

## 1. Create a free Neo4j AuraDB instance

1. Go to [console.neo4j.io](https://console.neo4j.io) and sign up (free tier).
2. Create a new **AuraDB Free** instance.
3. Download the credentials file it gives you (`NEO4J_URI`, `NEO4J_USERNAME`,
   `NEO4J_PASSWORD`). Keep it safe; the password is shown only once.
4. Wait a minute or two for the instance to finish starting (status "Running"
   in the console).

## 2. Load the graph

Open the Neo4j Browser for your instance (link in the Aura console) and paste
in the contents of [`cypher/load.cypher`](../cypher/load.cypher). It creates
the constraints, then loads every company, layer, technology, country, and
chokepoint, then all the relationships between them, straight from this
repo's CSVs on GitHub. Re-running it is safe.

## 3. Run your first screen

Still in Neo4j Browser, paste in
[`cypher/screens/01_single_source_chokepoints.cypher`](../cypher/screens/01_single_source_chokepoints.cypher).
It lists every chokepoint in the chip supply chain controlled by exactly one
company, the highest-conviction picks-and-shovels names. See
[`docs/screens.md`](screens.md) for what each screen finds and why it matters.

## 4. Ask Claude questions about the graph

See [`docs/mcp.md`](mcp.md) for how to connect Claude (Desktop or Code) to
your Aura instance and ask it questions in plain English.

## 5. Keep it updated automatically (optional)

The graph stays useful only if real news keeps getting added. Hermes Agent, a
free AI agent that runs on your own computer, can do the weekly pass for you:
it reads the week's news for the companies in your graph, proposes new
relationships, sends you the diff on Telegram, and writes to your Neo4j only
after you approve. It never deletes or edits anything already in the graph.

Six commands, in order, with the reasons for the order:
[`docs/hermes.md`](hermes.md). Telegram pairing is in
[`docs/telegram.md`](telegram.md).

## What's in this repo

See [`../CLAUDE.md`](../CLAUDE.md) for the full ontology and data rules.

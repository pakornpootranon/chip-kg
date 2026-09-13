# chip-kg

A small knowledge graph of the semiconductor industry (companies, supply chain
layers, technologies, countries, and chokepoints) built for relationship-based
stock screening. Query it by hand in the Aura Query editor or through Claude via MCP,
and let a daily Claude scheduled task feed news into it.

No engineering background required. Follow these steps in order.

What it costs: Neo4j AuraDB Free is free, no card. Steps 4 and 5 need a paid Claude plan (Pro or higher) because they use a custom connector.

## 1. Create a free Neo4j AuraDB instance

1. Go to [console.neo4j.io](https://console.neo4j.io) and sign up (free tier). Step-by-step: [`docs/aura.md`](aura.md).
2. Create a new **AuraDB Free** instance.
3. Download the credentials file it gives you (`NEO4J_URI`, `NEO4J_USERNAME`,
   `NEO4J_PASSWORD`). Keep it safe; the password is shown only once.
4. Wait a minute or two for the instance to finish starting (status "Running"
   in the console).

## 2. Load the graph

Open the Query editor for your instance (the Query button on the instance card in the Aura console) and paste
in the contents of [`cypher/load.cypher`](../cypher/load.cypher). It creates
the constraints, then loads every company, layer, technology, country, and
chokepoint, then all the relationships between them, straight from this
repo's CSVs on GitHub. Re-running it is safe.

## 3. Run your first screen

Still in the Query editor, paste in
[`cypher/screens/01_single_source_chokepoints.cypher`](../cypher/screens/01_single_source_chokepoints.cypher).
It lists every chokepoint in the chip supply chain controlled by exactly one
company, the highest-conviction picks-and-shovels names. See
[`docs/analysis.md`](analysis.md) for what each screen finds and why it matters, plus saved questions to paste into Claude.

## 4. Ask Claude questions about the graph

See [`docs/mcp.md`](mcp.md) for how to connect Claude (Desktop or Code) to
your Aura instance and ask it questions in plain English.

## 5. Keep it updated automatically (optional)

The graph stays useful only if real news keeps getting added. A daily Claude
scheduled task reads the last 24 hours of news for the companies in your
graph, adds each relevant item as a NewsItem linked to the companies and
chokepoints it touches, and writes you a short morning brief. It never deletes
or edits anything already in the graph.

Setup is in [`docs/schedule.md`](schedule.md). The cloud path (Cowork) has not yet been verified on follower plans; if it is not available to you, paste the same prompt into a normal chat each morning and you get the same brief.

## What's in this repo

See [`../CLAUDE.md`](../CLAUDE.md) for the full ontology and data rules.

# Ask Claude questions about the graph

Once you've loaded the graph into your AuraDB Free instance (step 2 in
[`README.md`](README.md)), you can connect Claude to it and ask questions in
plain English instead of writing Cypher yourself.

This uses the official Neo4j MCP server, package name **`mcp-neo4j-cypher`**
(confirmed on PyPI, latest `0.6.0` as of this writing). It runs locally on
your machine and talks to your Aura instance over the internet. Nothing
about your graph is sent anywhere except Neo4j and, when you ask a question,
whichever Claude product you're using.

You'll need [`uv`](https://docs.astral.sh/uv/) installed (`uvx` ships with
it) so the server can be run without a manual `pip install`.

## Claude Desktop

Edit your Claude Desktop config file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add this under `mcpServers` (create the file/key if it doesn't exist), using
the credentials from your Aura instance:

```json
{
  "mcpServers": {
    "neo4j-cypher": {
      "command": "uvx",
      "args": ["mcp-neo4j-cypher"],
      "env": {
        "NEO4J_URI": "neo4j+s://xxxxxxxx.databases.neo4j.io",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "your-password",
        "NEO4J_DATABASE": "neo4j"
      }
    }
  }
}
```

Restart Claude Desktop after saving.

## Claude Code

From the command line, in any directory:

```bash
claude mcp add neo4j-cypher -s user \
  -e NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io \
  -e NEO4J_USERNAME=neo4j \
  -e NEO4J_PASSWORD=your-password \
  -e NEO4J_DATABASE=neo4j \
  -- uvx mcp-neo4j-cypher
```

`-s user` makes it available in every project, not just this one. Run
`claude mcp list` to confirm it connected.

## What Claude can do once connected

Two tools show up: one that reads the graph's schema (labels, relationship
types, properties) and one that runs a read Cypher query you or Claude
writes. Claude reads the schema first, then writes Cypher against it, so you
don't need to teach it the ontology by hand, though pointing it at
[`../CLAUDE.md`](../CLAUDE.md) helps it use the Tier/Layer conventions
correctly rather than guessing.

A known quirk: on first connecting, Claude may call the schema tool with no
sample size and get a Cypher syntax error back (`Variable 'None' not
defined`). That's a bug in the MCP server itself, not something wrong with
your graph. Claude recovers on retry by passing an explicit sample size, or
you can just ask it again.

## Three demo questions

These were run blind: a fresh Claude session was given nothing but the
ontology above (not this repo's `cypher/screens/` files) and wrote each
query on its first attempt.

### 1. "Which chokepoints in this graph are controlled by only one company?"

```cypher
MATCH (c:Company)-[:CONTROLS]->(ch:Chokepoint)
WITH ch, count(DISTINCT c) AS numControllers, collect(c.name) AS companies
WHERE numControllers = 1
RETURN ch.name AS chokepoint, companies
```

| chokepoint | controlled by |
|---|---|
| EUV Lithography | ASML |
| Advanced Foundry (<7nm) | TSMC |
| HBM Memory | SK Hynix |

Clean on the first try, and this is screen `01_single_source_chokepoints` in
plain English, a good first question to ask because you can check Claude's
answer against that file yourself.

### 2. "If NVIDIA's demand keeps growing, which listed companies within two supply hops upstream of NVIDIA would benefit, grouped by supply-chain layer?"

```cypher
MATCH path = (upstream:Company)-[:SUPPLIES*1..2]->(nvidia:Company {name: "NVIDIA"})
WHERE upstream.listed = true
MATCH (upstream)-[:OPERATES_IN]->(l:Layer)
RETURN l.name AS layer, l.order AS layerOrder, collect(DISTINCT upstream.name) AS companies
ORDER BY layerOrder
```

| layer | companies |
|---|---|
| Foundry | TSMC |
| IDM | Micron Technology |
| Memory | SK Hynix |

Also correct, and the result is economically sensible (foundry and memory
inputs upstream of a fabless GPU designer), which is exactly why it's worth
flagging what Claude did NOT check before trusting that: it assumed
`SUPPLIES` points from supplier to customer and walked it backwards from
NVIDIA without confirming that direction against the schema, and it matched
the string `"NVIDIA"` without first looking up the exact name stored on the
node. Both guesses happened to be right here. The tell that they weren't
would have been an empty result, or an implausible layer like `EndDemand`
showing up "upstream". If you ever see that, ask Claude to check the
relationship direction and the exact company name before trusting the
answer.

### 3. "Which layer of the chip supply chain is most concentrated in a single country, and which country is it?"

```cypher
MATCH (c:Company)-[:OPERATES_IN]->(l:Layer)
MATCH (c)-[:HQ_IN]->(country:Country)
WITH l, country, count(DISTINCT c) AS numCompanies
WITH l, collect({country: country.name, numCompanies: numCompanies}) AS countryCounts, sum(numCompanies) AS totalCompanies
UNWIND countryCounts AS cc
WITH l, totalCompanies, cc
ORDER BY cc.numCompanies DESC
WITH l, totalCompanies, collect(cc)[0] AS topCountry
RETURN l.name AS layer, topCountry.country AS country, topCountry.numCompanies AS companiesInCountry, totalCompanies,
       toFloat(topCountry.numCompanies) / totalCompanies AS concentration
ORDER BY concentration DESC
```

| layer | top country | companies | of layer total | concentration |
|---|---|---|---|---|
| Materials | Japan | 4 | 4 | 100% |
| EndDemand | United States | 3 | 3 | 100% |
| EDA | United States | 2 | 3 | 67% |
| IDM | United States | 5 | 8 | 63% |
| Fabless | United States | 5 | 8 | 63% |
| Equipment | United States | 4 | 7 | 57% |
| Memory | Taiwan | 2 | 5 | 40% |
| Foundry | United States | 1 | 3 | 33% |
| Packaging | United States | 1 | 3 | 33% |

(One layer, IP, has zero companies mapped to it yet via `OPERATES_IN`, a
gap in the seed data, listed in `data/GAPS.md`, not a query bug.)

This is the question that actually caught something. Materials (Japan) and
EndDemand (United States) are tied at 100% concentration, and the question
as asked ("which layer", singular) doesn't say how to break a tie. A first
attempt that added `ORDER BY concentration DESC LIMIT 1` would have silently
picked whichever of the two Neo4j happened to return first and reported it
as *the* answer, with no indication a tie was ever there. The honest version
of this query stops at the ranked table and states the tie; if you want a
single name, you need a reason to prefer one (here, Materials has more
companies backing the same 100% figure, 4 versus 3, for whatever that's
worth). The lesson for using Claude on this graph generally: normalizing a
share within each group is necessary to get a correct ranking, but it is not
sufficient to collapse that ranking to one answer. Watch for Claude adding
a `LIMIT 1` that quietly resolves a tie you were never told about.

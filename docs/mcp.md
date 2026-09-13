# Ask Claude questions about the graph

Once the graph is loaded (see [`aura.md`](aura.md)), connect Claude to your Aura instance and ask questions in plain English. Claude reads the schema, writes the Cypher, runs it and explains the answer.

**Does the hosted server let Claude write to the graph?** Yes, but only if you turn it on. MCP for Aura exposes three tools: get schema, read (read-only Cypher) and a separate read-write tool that is off by default. Leave it off for asking questions. The daily news task ([`schedule.md`](schedule.md)) needs it on, because it adds NewsItem nodes. Nothing in this repo ever deletes or edits existing Company nodes or edges, on or off.

## Path A: MCP for Aura (recommended, nothing to install)

Neo4j runs an MCP server for every Aura instance, including Free. You add its URL to Claude as a custom connector and log in with your Aura account. No password goes into any config file.

### 1. Find your instance's MCP URL

In the [Aura console](https://console.neo4j.io) go to **Instances**, open the **[...]** menu on your instance and choose **Inspect**. The panel shows the MCP server URL. It always has this shape, where the instance id is the eight characters at the start of your connection URI:

```
https://<INSTANCE_ID>.mcp-instances.neo4j.io
```

Screenshot placeholder: `docs/img/mcp-01-inspect.png` (Inspect panel with the MCP URL).

### 2. Add it to Claude

**Claude Desktop or claude.ai:** Settings, then **Connectors**, then **Add custom connector**. Name it `chip-kg`, paste the URL, click **Add**. Then click **Connect**. A browser tab opens on the Aura login page; sign in with the same account you used to create the instance and approve. Back in Claude the connector shows as connected.

Screenshot placeholder: `docs/img/mcp-02-add-connector.png` (Add custom connector dialog).
Screenshot placeholder: `docs/img/mcp-03-aura-login.png` (Aura consent page).

Custom connectors need a paid Claude plan (Pro, Max, Team or Enterprise).

**Claude Code:** from a terminal:

```bash
claude mcp add --transport http chip-kg https://<INSTANCE_ID>.mcp-instances.neo4j.io
claude mcp list
```

Then inside a Claude Code session type `/mcp`, pick `chip-kg` and follow the login link.

### 3. Turn on the connector in a chat

Start a new chat, open the tools menu (the plus or sliders icon under the message box) and make sure `chip-kg` is enabled. Then ask a question. The first time, Claude will call the schema tool; that is normal.

### If the instance is paused

Aura Free pauses after a few days without use. The connector then fails to connect. Open the console, click **Resume** on the instance, wait a minute, try again.

## Path B: run the MCP server yourself (fallback)

Use this if custom connectors are not available on your plan, or if you want the graph in Claude Code without OAuth. It runs Neo4j's open-source `mcp-neo4j-cypher` server on your computer with [`uv`](https://docs.astral.sh/uv/) installed.

**Claude Desktop:** edit the config file (macOS `~/Library/Application Support/Claude/claude_desktop_config.json`, Windows `%APPDATA%\Claude\claude_desktop_config.json`) and add, with your own credentials:

```json
{
  "mcpServers": {
    "chip-kg": {
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

Restart Claude Desktop.

**Claude Code:**

```bash
claude mcp add chip-kg -s user \
  -e NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io \
  -e NEO4J_USERNAME=neo4j \
  -e NEO4J_PASSWORD=your-password \
  -e NEO4J_DATABASE=neo4j \
  -- uvx mcp-neo4j-cypher
```

Two quirks of this server, seen while building the repo. On the first schema call Claude may get an error about a `None` variable; it recovers by retrying with a sample size. And its write tool refuses schema statements like `CREATE CONSTRAINT`, while its read tool happens to run them. Use `scripts/load.py` or the Aura query editor for constraints.

## Three worked examples

Each was run against the loaded graph on 2026-09-13. Ask the question as written and you should get the same numbers until the data changes.

### 1. "Which chokepoints are controlled by only one company?"

Cypher Claude wrote:

```cypher
MATCH (c:Company)-[r:CONTROLS]->(cp:Chokepoint)
WITH cp, collect(c.name) AS controllers, collect(r.confidence) AS confidence, count(c) AS n
WHERE n = 1
RETURN cp.name AS chokepoint, cp.layer AS layer, controllers[0] AS controlled_by, confidence[0] AS confidence
ORDER BY layer, chokepoint
```

| chokepoint | layer | controlled by | confidence |
|---|---|---|---|
| EUV Lithography | Equipment | ASML | high |
| EUV Mask Inspection | Equipment | Lasertec | medium |
| ABF Substrate Film | Materials | Ajinomoto | medium |

This is screen 01 in plain English, so you can check the answer against `cypher/screens/01_single_source_chokepoints.cypher` yourself. Notice that Advanced Foundry and HBM Memory no longer appear: Samsung and Micron were added as second controllers in v2, at medium confidence. Whether that is the right call is a data question, not a query question; see `data/GAPS.md`.

### 2. "If NVIDIA's demand keeps growing, which companies within two supply hops upstream of NVIDIA benefit, grouped by layer?"

```cypher
MATCH (supplier:Company)-[:SUPPLIES*1..2]->(target:Company {name: "NVIDIA"})
WHERE supplier <> target
WITH DISTINCT supplier
MATCH (supplier)-[:OPERATES_IN]->(layer:Layer)
RETURN layer.name AS layer, layer.order AS layer_order,
       collect(DISTINCT supplier.name + " (T" + toString(supplier.tier) + ")") AS companies
ORDER BY layer_order
```

Fifty-three companies across nine layers. Foundry is TSMC alone. Memory is SK Hynix and Micron. Equipment has nineteen names, from ASML and Lasertec (Tier 1) through Advantest, Lam, KLA and Tokyo Electron (Tier 2) to Camtek and FormFactor (Tier 3). Materials has sixteen, including HOYA and Ajinomoto at Tier 1. Packaging shows ASE, Amkor and the substrate makers Ibiden, Unimicron and Nan Ya PCB.

Two things Claude did not check before trusting this. It assumed SUPPLIES points from supplier to customer, and it matched the string "NVIDIA" without first looking up the exact name on the node. Both happened to be right. The tell that they were not would be an empty result, or EndDemand names showing up "upstream". If you see that, ask Claude to confirm the relationship direction and the exact company name.

### 3. "Which layer is most concentrated in a single country?"

```cypher
MATCH (c:Company)-[:OPERATES_IN]->(l:Layer), (c)-[:HQ_IN]->(cn:Country)
WITH l, cn, count(c) AS n
WITH l, collect({country: cn.name, count: n}) AS breakdown, sum(n) AS total
UNWIND breakdown AS b
RETURN l.name AS layer, b.country AS country, b.count AS companies,
       round(100.0 * b.count / total) AS pct_of_layer
ORDER BY l.order, pct_of_layer DESC
```

Top country per layer:

| layer | top country | share of layer |
|---|---|---|
| EndDemand | United States | 83% |
| Packaging | Taiwan | 62% |
| IDM | United States | 58% |
| EDA | United States | 57% |
| IP | United States | 50% |
| Fabless | United States | 49% |
| Materials | Japan | 43% |
| Equipment | United States | 41% |
| Foundry | Taiwan | 40% |
| Memory | Taiwan | 38% |

The question says "which layer", singular, and an eager query adds `LIMIT 1` and returns EndDemand. That answer is technically right and economically useless: the hyperscalers being American is not a supply-chain risk. The interesting rows are Packaging (Taiwan 62%) and Foundry (Taiwan 40% by count, but TSMC alone is most of the world's advanced capacity). Two lessons. Headquarters count is not capacity share; read `fab_or_ops_geography` and the CONTROLS edges for that. And watch for Claude collapsing a ranked table to one row when the question deserves the whole table.

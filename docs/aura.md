# Load the graph into Neo4j AuraDB Free

Ten minutes, no software to install. You need a browser and a free Neo4j account.

## 1. Create a free instance

1. Go to [console.neo4j.io](https://console.neo4j.io) and sign up. Google or email login both work. No credit card.
2. Click **Create instance**. Pick **AuraDB Free**. Give it a name like `chip-kg`. Leave the region and dataset options as they are (choose "empty" if it asks about a starter dataset).
3. A dialog shows your connection details: **URI**, **Username** (`neo4j`) and a generated **Password**. Click **Download** to save the credentials file. This is the only time the password is shown. If you lose it you can reset it from the instance menu later.
4. Wait until the instance card says **Running**. This takes one to three minutes.

Screenshots are being added under `docs/img/`; the text is complete without them.

Screenshot placeholder: `docs/img/aura-01-create.png` (Create instance dialog with AuraDB Free selected).
Screenshot placeholder: `docs/img/aura-02-credentials.png` (credentials dialog with the Download button).

## 2. Open the Query editor

1. On the instance card click **Query**. The Query editor opens in a new tab. Every doc in this repo calls it the Query editor.
2. It may ask you to connect. Use the username and password from step 1.

Screenshot placeholder: `docs/img/aura-03-open.png` (instance card with the Query button).

## 3. Paste the loader

1. Open [`cypher/load.cypher`](../cypher/load.cypher) on GitHub, click **Raw**, select all and copy.
2. Paste the whole thing into the query box at the top of the editor and press the play button (or Ctrl+Enter / Cmd+Enter).
3. The editor runs the statements one after another. It takes about a minute. The last statement prints a row with `nodes` and `edges`. Expect **216 nodes** and **869 edges**.

Screenshot placeholder: `docs/img/aura-04-paste.png` (query box with load.cypher pasted).
Screenshot placeholder: `docs/img/aura-05-counts.png` (result row showing 216 and 869).

If you see fewer edges than expected, run the loader again. It is safe: every statement uses `MERGE`, so nothing is duplicated.

If the editor runs only the first statement, run the file in pieces: the constraints block, then each LOAD CSV block, in order.

## 4. Try one query

Paste this to see the chokepoints and who controls them:

```cypher
MATCH (c:Company)-[:CONTROLS]->(cp:Chokepoint)
RETURN cp.name AS chokepoint, collect(c.name) AS controlled_by
ORDER BY size(controlled_by), chokepoint;
```

Then go to [`docs/mcp.md`](mcp.md) (needs a paid Claude plan) to connect Claude to the graph and ask questions in plain language.

## Starting over

To wipe the instance and reload, paste [`cypher/reset.cypher`](../cypher/reset.cypher) and run it, then paste `load.cypher` again.

## Loading from your own computer instead (author path)

Followers can skip this. If you cloned the repo and have Python 3.11 or later:

```
pip install -r requirements.txt
cp <your downloaded credentials file> .env
python scripts/load.py
```

`scripts/load.py --reset` wipes and reloads. `scripts/load.py --counts` prints the counts only.

## Limits of the Free tier

One instance per account, 200,000 nodes and 400,000 relationships. This graph uses well under one percent of that. The instance pauses after a few days without use; open the console and click **Resume** to wake it, and the MCP connection will work again.

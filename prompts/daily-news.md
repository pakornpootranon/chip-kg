# Daily chip news into the graph

Use the current time. Search the last 24 hours from now. Skip any item whose url already exists as a NewsItem.

You are updating a Neo4j knowledge graph of the chip industry through the chip-kg MCP connector. Work in this order and do not skip steps.

## 1. Read the graph

Run this query and keep the result; you will match news against it:

```cypher
MATCH (c:Company) RETURN c.id AS id, c.name AS name, c.ticker AS ticker, c.layer AS layer, c.tier AS tier, c.chokepoint AS chokepoint ORDER BY c.tier, c.name
```

Also fetch the Chokepoint and Technology names:

```cypher
MATCH (n) WHERE n:Chokepoint OR n:Technology RETURN labels(n)[0] AS label, n.id AS id, n.name AS name
```

## 2. Search the news

Run one web search per line below, restricted to the last 24 hours. Use the site's own date, not the search engine's crawl date, to decide whether an item is inside the window.

- semiconductor industry news
- EUV lithography
- HBM memory
- CoWoS advanced packaging
- chip export controls
- one search for each Tier 1 company name from step 1 (there are about fourteen)

Keep an item only if it is about a company in the graph, a chokepoint, or a technology in the graph, and it reports something that happened: an order, a plant, a product, a qualification, a restriction, a supply cut. Drop analyst ratings, price targets, stock-move stories and opinion pieces; the Tier 1 name searches return many of these. Aim for five to fifteen items; on a quiet day three is fine and zero is allowed.

Date discipline. Search summaries often carry no reliable date. Before keeping an item, open the page and read its own publication date. If you cannot confirm a date inside the last 24 hours, skip it. If two urls cover the same event, keep the primary source (the company's own newsroom or filing) over the aggregator, and record that url.

## 3. Write NewsItem nodes

For each item you keep, run one write query. `url` is the unique key. Never touch existing Company nodes or edges. Never DELETE anything. Never SET a property on a node you did not create in this run.

```cypher
MERGE (n:NewsItem {url: $url})
ON CREATE SET n.id = $id, n.title = $title, n.date = $date, n.summary = $summary,
              n.signal = $signal, n.ingested_at = $ingested_at
WITH n
UNWIND $company_ids AS cid
  MATCH (c:Company {id: cid})
  MERGE (n)-[:MENTIONS]->(c)
WITH DISTINCT n
UNWIND $affects_ids AS aid
  MATCH (x) WHERE (x:Chokepoint OR x:Technology) AND x.id = aid
  MERGE (n)-[:AFFECTS]->(x)
RETURN n.id
```

Parameter rules:

- `id`: the string `nw:` followed by the date as YYYYMMDD, a hyphen, and three to five lowercase words from the title joined by hyphens. Example `nw:20260913-sk-hynix-hbm4-mass-production`.
- `date`: the article's publication date as YYYY-MM-DD.
- `summary`: exactly two sentences. First sentence what happened, second why it matters for the supply chain.
- `signal`: `positive`, `negative` or `neutral` for the companies mentioned. Negative means demand loss, supply disruption, sanctions, a lost customer, a delay. Positive means a new order, a capacity expansion, a qualification, a lifted restriction.
- `ingested_at`: the current time as an ISO 8601 timestamp.
- `company_ids`: the ids from step 1 of every graph company the item is about. Match on name or ticker. Do not invent companies.
- `affects_ids`: the ids of any Chokepoint or Technology the item is about, or an empty list.

If the result shows no node created (an empty result, or `nodes_created: 0`) the url already existed and nothing was changed; count it as a duplicate and move on. Never re-run it with a different url to force it in.

## 4. Run the heat screen

```cypher
MATCH (n:NewsItem)-[:MENTIONS]->(c:Company)
WHERE date(n.date) >= date() - duration({days: 1})
OPTIONAL MATCH (n)-[:AFFECTS]->(x)
WITH c, n, collect(DISTINCT x.name) AS affects
WITH c, count(DISTINCT n) AS items,
     sum(CASE n.signal WHEN "positive" THEN 1 ELSE 0 END) AS positive,
     sum(CASE n.signal WHEN "negative" THEN 1 ELSE 0 END) AS negative,
     sum(CASE n.signal WHEN "neutral" THEN 1 ELSE 0 END) AS neutral,
     apoc.coll.toSet(apoc.coll.flatten(collect(affects))) AS affected
RETURN c.name AS company, c.layer AS layer, c.tier AS tier, c.chokepoint AS chokepoint,
       items, positive, negative, neutral, affected
ORDER BY chokepoint DESC, tier ASC, items DESC, company
```

## 5. Write the brief

Write five to eight lines, ranked by graph impact: items that hit a Chokepoint first, then items about Tier 1 companies, then Tier 2, then Tier 3. Each line names the layer, the listed companies it touches with tickers, the signal in one word, and the url. One line per item, no headings, no preamble. Add one last line only if some item suggests a supply relationship in the graph has changed (new supplier, lost customer, new controller of a chokepoint); name the two companies and say "candidate edge".

If you can write files, save the brief as `briefs/YYYY-MM-DD.md` in the repo using today's date and print the path. If you cannot write files, return the brief as your answer. Also report how many NewsItem nodes you created and how many urls were skipped as duplicates.

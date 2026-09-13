# Compare two names on the graph

Paste into Claude Desktop with the Neo4j connector on. Replace the two company names.

---

Compare Lam Research and Tokyo Electron using only the Neo4j graph.

Fetch the schema first. Find both Company nodes by name or ticker. Then, showing the Cypher, build one comparison table with these rows:

- Layer, sub-segment, tier, chokepoint flag, headquarters country
- Fab or operations geography (the list on the node)
- Number of Companies each one SUPPLIES, and the names
- Number of Companies that SUPPLY each one, and the names
- Chokepoints each one CONTROLS
- Technologies each one DEPENDS_ON
- Companies each one COMPETES_WITH
- Customers they share (Companies both of them SUPPLY)
- Customers only one of them has

Then write five or six sentences: where their positions overlap, where one has a relationship the other lacks, which one sits closer to a single-source chokepoint, and which one is more concentrated on a single customer or country by the graph's count. Use the description and key_products properties for context. No prices, no recommendations. If the two are not in the same layer, say so up front and explain what the comparison can and cannot tell you.

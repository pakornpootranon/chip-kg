# What breaks if X stops shipping?

Paste into Claude Desktop with the Neo4j connector on. Replace the company name.

---

Suppose ASML stopped shipping for a year.

Use the Neo4j graph. Fetch the schema first. Find the Company node by name or ticker.

Then answer in this order, showing the Cypher for each step:

1. Direct customers: every Company that this company SUPPLIES, with their layer and tier.
2. Second-order customers: every Company those direct customers SUPPLY, grouped by layer, with the path in words (for example ASML supplies TSMC, TSMC supplies NVIDIA).
3. Chokepoints and technologies: any Chokepoint this company CONTROLS and any Technology that the affected customers DEPEND_ON.
4. Substitutes: every Company that COMPETES_WITH this company, with their layer and country. Say whether each one controls the same Chokepoint.

Then write a plain-English brief of at most eight lines: which listed names are hit first, which are hit second, whether any substitute exists in the graph, and where the graph's data is thin (edges with confidence medium or low, or an obviously missing supplier). Do not speculate beyond what the graph shows; label any outside knowledge you add as such.

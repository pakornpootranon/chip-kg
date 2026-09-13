# Which of my holdings share a chokepoint?

Paste into Claude Desktop with the Neo4j connector on. Replace the list of holdings with your own company names or tickers.

---

I hold these chip stocks: NVIDIA, ASML, SK Hynix, Advantest, HOYA.

Use the Neo4j graph. First fetch the schema. Then, for each holding, find the Company node by name or ticker (tickers are Yahoo style, for example 2330.TW).

For every pair of my holdings, tell me whether they are connected through a Chokepoint in any of these ways:

1. Both CONTROL the same Chokepoint.
2. One CONTROLS a Chokepoint and the other SUPPLIES it or is supplied by it, within two SUPPLIES hops.
3. Both DEPEND_ON the same Technology.

Show the Cypher you ran. Then give me a table with one row per pair that is connected: the two holdings, the chokepoint or technology, the path in words, and the lowest confidence value along the path.

Finish with two or three sentences on which single chokepoint or technology my portfolio leans on most, counting how many holdings touch it. Do not give price targets or recommendations. Say clearly if a holding could not be found in the graph.

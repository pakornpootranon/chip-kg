# Which of my holdings share a chokepoint?

Paste into Claude Desktop with the chip-kg connector on. Replace the list of holdings with your own company names or tickers.

Copy everything below this line.

I hold these chip stocks: NVIDIA, ASML, SK Hynix, Advantest, HOYA.

Use the Neo4j graph. First fetch the schema (if the schema tool errors, retry it with a sample size). Then, for each holding, find the Company node by name or ticker (tickers are Yahoo style, for example 2330.TW).

For every pair of my holdings, tell me whether they are connected through a Chokepoint in any of these ways:

1. Both CONTROL the same Chokepoint.
2. One CONTROLS a Chokepoint and there is a directed SUPPLIES path of one or two hops between the two holdings, in either direction (A supplies B, or A supplies X which supplies B). Two holdings that merely share a customer do not count.
3. Both DEPEND_ON the same Technology.

If a test finds nothing, say so in one line rather than leaving it out.

Show the Cypher you ran. Then give me a table with one row per pair that is connected: the two holdings, the chokepoint or technology, the path in words, and the lowest confidence value along the path.

Finish with two or three sentences on which single chokepoint or technology my portfolio leans on most, counting how many holdings touch it. Do not give price targets or recommendations. Say clearly if a holding could not be found in the graph.

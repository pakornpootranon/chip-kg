# What changed this week?

Paste into Claude Desktop with the chip-kg connector on. Needs NewsItem nodes, which the daily task adds (docs/schedule.md). Before the task has run, this returns nothing.

Copy everything below this line.

Use the current date. Look at the last 7 days in the Neo4j graph.

Fetch the schema first (if the schema tool errors, retry it with a sample size). NewsItem.date is a string in YYYY-MM-DD form and signal is lowercase, one of positive, negative, neutral. If the graph has no NewsItem nodes, say so in one line and stop. Then, showing the Cypher:

1. List every NewsItem with date in the last 7 days: title, date, signal, url, the Companies it MENTIONS and the Chokepoints or Technologies it AFFECTS.
2. Rank the mentioned Companies by number of items, split into positive, negative and neutral. Include each company's layer, tier and chokepoint flag.
3. List any Chokepoint or Technology hit by two or more items this week.

Then write a brief of five to eight lines, ordered by graph impact: chokepoint hits first, then Tier 1 names, then Tier 2, then Tier 3. Each line names the layer and the listed companies involved and links the item. Use the summary property on each NewsItem; do not re-search the web. End with one line on which relationships in the graph these items suggest may have changed (a new supplier, a lost customer, a new controller of a chokepoint), so I can decide whether to update the CSVs. Do not change anything in the graph.

// SCREEN 03: Country concentration by layer
//
// What it finds: for each supply-chain Layer, the share of Companies
// headquartered in each Country, biggest first.
//
// Why an investor cares: this is the geographic risk map in one query. It
// shows which layers depend on one country's politics, weather and export
// rules, and which are genuinely spread out.
//
// What a hit does not mean: headquarters is not manufacturing footprint. A
// US-headquartered fabless company makes everything in Taiwan. Read the
// fab_or_ops_geography list on each Company for where the plants are, and
// the SUPPLIES edges for where the exposure really sits.

MATCH (c:Company)-[:OPERATES_IN]->(l:Layer), (c)-[:HQ_IN]->(cn:Country)
WITH l, cn, count(c) AS n
WITH l, collect({country: cn.name, count: n}) AS breakdown, sum(n) AS total
UNWIND breakdown AS b
RETURN l.name AS layer, l.order AS layer_order, b.country AS country, b.count AS companies,
       round(100.0 * b.count / total) AS pct_of_layer
ORDER BY layer_order, pct_of_layer DESC;

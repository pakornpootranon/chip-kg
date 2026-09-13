// SCREEN: Country concentration by layer
//
// What it finds: for each supply-chain Layer, the share of Companies
// headquartered in each Country.
//
// Why an investor cares: this is the geographic-risk map in one query —
// which layers of the chain are dominated by one country (and therefore
// exposed to that country's politics, disasters, or export rules) versus
// which layers are genuinely diversified.
//
// What a hit does NOT mean: HQ country is not the same as manufacturing
// footprint — a US-headquartered company can still fab or assemble
// entirely overseas (see any Fabless company's SUPPLIES edges for its real
// manufacturing exposure). This screen is about corporate domicile, one
// input into geographic risk, not the whole picture.

MATCH (c:Company)-[:OPERATES_IN]->(l:Layer), (c)-[:HQ_IN]->(co:Country)
WITH l, co, count(c) AS n
WITH l, collect({country: co.name, count: n}) AS breakdown, sum(n) AS total
UNWIND breakdown AS b
RETURN l.name AS layer, l.order AS layer_order, b.country AS country, b.count AS companies,
       round(100.0 * b.count / total) AS pct_of_layer
ORDER BY layer_order, pct_of_layer DESC;

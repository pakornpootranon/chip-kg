// SCREEN 02: Upstream of a company
//
// What it finds: every Company within two SUPPLIES hops upstream of a named
// company (who supplies it, and who supplies those suppliers), grouped by
// supply-chain Layer. Every Company in this graph is listed, so every hit
// is a stock you can buy.
//
// Why an investor cares: this answers "who benefits if this company's demand
// keeps growing" using relationships instead of financial ratios. A name two
// hops out is a less obvious, less crowded way to get exposure to the same
// demand driver.
//
// What a hit does not mean: distance in the graph says nothing about revenue
// materiality. A two-hop supplier might get one percent or ninety percent of
// its sales from that path. A short list means few suppliers are mapped yet,
// not that the company has few suppliers.
//
// Usage: set $company_name to the exact Company name, e.g. "NVIDIA".
:param company_name => "NVIDIA";

MATCH (supplier:Company)-[:SUPPLIES*1..2]->(target:Company {name: $company_name})
WHERE supplier <> target
WITH DISTINCT supplier
MATCH (supplier)-[:OPERATES_IN]->(layer:Layer)
RETURN layer.name AS layer, layer.order AS layer_order,
       collect(DISTINCT supplier.name + " (T" + toString(supplier.tier) + ")") AS companies
ORDER BY layer_order;

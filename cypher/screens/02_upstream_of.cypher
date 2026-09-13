// SCREEN: Upstream of a company
//
// What it finds: every listed Company within two SUPPLIES hops upstream of
// a named target company (i.e. who supplies the target, and who supplies
// those suppliers), grouped by supply-chain Layer.
//
// Why an investor cares: this answers "who benefits if [company]'s demand
// grows?" without relying on financial ratios — it's the relationship-based
// screening this whole graph exists for. A name showing up two hops out is
// a less obvious, less crowded way to get exposure to the same demand
// driver as the target company.
//
// What a hit does NOT mean: proximity in the graph is not the same as
// revenue materiality — a supplier could source 1% or 90% of a customer's
// input from a two-hop name, and this screen can't tell you which. It also
// only shows what's HIGH/MEDIUM/LOW confidence and sourced in this graph
// today; a thin result for a company just means its suppliers aren't
// mapped yet, not that it has no suppliers in reality.
//
// Usage: set $company_name to the target, e.g. "NVIDIA".
:param company_name => "NVIDIA";

MATCH path = (supplier:Company)-[:SUPPLIES*1..2]->(target:Company {name: $company_name})
WHERE supplier.listed = true
WITH DISTINCT supplier
MATCH (supplier)-[:OPERATES_IN]->(layer:Layer)
RETURN layer.name AS layer, layer.order AS layer_order, collect(DISTINCT supplier.name) AS companies
ORDER BY layer_order;

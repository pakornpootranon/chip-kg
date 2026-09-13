// SCREEN 04: Tier 2 companies feeding Tier 1
//
// What it finds: Tier 2 Companies ranked by how many Tier 1 Companies they
// SUPPLY, with the Tier 1 names listed.
//
// Why an investor cares: a Tier 2 name (a critical supplier with a few
// credible competitors) that feeds several Tier 1 chokepoint controllers
// rides their pricing power without carrying the same single-source risk
// itself. Often a better risk-adjusted way to play the same theme.
//
// What a hit does not mean: a low count means few SUPPLIES edges are mapped
// for that company, not that it has few Tier 1 customers in reality. Tier is
// a judgment call (see CLAUDE.md), so a company you think of as Tier 2 may be
// filed under Tier 3 here. Check data/universe.csv.

MATCH (t2:Company {tier: 2})-[:SUPPLIES]->(t1:Company {tier: 1})
WITH t2, count(DISTINCT t1) AS n, collect(DISTINCT t1.name) AS tier1_customers
MATCH (t2)-[:OPERATES_IN]->(l:Layer)
RETURN t2.name AS tier2_company, l.name AS layer, n AS tier1_customers_count, tier1_customers
ORDER BY n DESC, tier2_company;

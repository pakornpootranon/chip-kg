// SCREEN: Tier 2 companies feeding Tier 1
//
// What it finds: Tier 2 Companies ranked by how many SUPPLIES edges they
// have running into Tier 1 Companies.
//
// Why an investor cares: a Tier 2 name (a critical supplier with a few
// credible competitors, per CLAUDE.md's tier rule) that feeds multiple
// Tier 1 chokepoint-controllers is riding the pricing power of the Tier 1
// names above it without carrying the same single-source concentration
// risk itself — often a better risk-adjusted way to play the same theme.
//
// What a hit does NOT mean: a low or zero count here does not mean a Tier 2
// company has no Tier 1 customers in reality — it means no SUPPLIES edge
// for that relationship has been added to the graph yet. This graph starts
// thin (see data/GAPS.md); expect this screen to get more interesting as
// more supplier relationships are added.

MATCH (t2:Company {tier: 2})-[:SUPPLIES]->(t1:Company {tier: 1})
RETURN t2.name AS tier2_company, count(t1) AS supplies_into_tier1, collect(t1.name) AS tier1_customers
ORDER BY supplies_into_tier1 DESC;

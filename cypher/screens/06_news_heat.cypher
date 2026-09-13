// SCREEN 06: News heat
//
// What it finds: Companies ranked by how many NewsItem nodes MENTION them in
// the last $days days, split into positive, negative and neutral counts,
// with the Chokepoints or Technologies those items AFFECT.
//
// Why an investor cares: this is where the daily news task lands. A Tier 1
// name with a burst of negative items, or a Chokepoint hit by several items
// in one week, is the graph telling you where to look first this morning.
//
// What a hit does not mean: counts measure attention, not importance, and
// the signal is Claude's one-word read of each headline. Open the items
// (url is on each NewsItem) before acting. An empty result means the daily
// task has not run yet or found nothing in the window, not that nothing
// happened.
//
// Usage: set $days to the window, e.g. 7.
:param days => 7;

MATCH (n:NewsItem)-[:MENTIONS]->(c:Company)
WHERE date(n.date) >= date() - duration({days: $days})
OPTIONAL MATCH (n)-[:AFFECTS]->(x)
WITH c, n, collect(DISTINCT x.name) AS affects
WITH c, count(DISTINCT n) AS items,
     sum(CASE n.signal WHEN "positive" THEN 1 ELSE 0 END) AS positive,
     sum(CASE n.signal WHEN "negative" THEN 1 ELSE 0 END) AS negative,
     sum(CASE n.signal WHEN "neutral" THEN 1 ELSE 0 END) AS neutral,
     apoc.coll.toSet(apoc.coll.flatten(collect(affects))) AS affected
RETURN c.name AS company, c.layer AS layer, c.tier AS tier, c.chokepoint AS chokepoint,
       items, positive, negative, neutral, affected
ORDER BY chokepoint DESC, tier ASC, items DESC, company;

// chip-kg reset. Deletes every node and relationship, including NewsItem
// nodes added by the daily task. Paste into the Query editor to start over,
// then run load.cypher again.
// Constraints are kept; load.cypher re-creates them with IF NOT EXISTS anyway.

MATCH (n) DETACH DELETE n;

// chip-kg reset — deletes every node and relationship in the database.
// Paste into Neo4j Browser to start over before re-running load.cypher.
// Does NOT drop constraints (load.cypher re-creates them with IF NOT EXISTS anyway).

MATCH (n) DETACH DELETE n;

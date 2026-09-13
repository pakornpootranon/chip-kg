// chip-kg loader. Paste this whole file into the Neo4j Browser query box for
// your Aura instance and run it. It reads the CSVs straight from GitHub.
// Safe to run again: everything is MERGE, nothing is CREATE or DELETE.
//
// If you forked the repo, change the username in raw_base to your own.
:param raw_base => "https://raw.githubusercontent.com/pakornpootranon/chip-kg/main";

// ---- constraints (same as cypher/constraints.cypher) ----
CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT layer_id IF NOT EXISTS FOR (l:Layer) REQUIRE l.id IS UNIQUE;
CREATE CONSTRAINT layer_name IF NOT EXISTS FOR (l:Layer) REQUIRE l.name IS UNIQUE;
CREATE CONSTRAINT technology_id IF NOT EXISTS FOR (t:Technology) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT technology_name IF NOT EXISTS FOR (t:Technology) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT country_id IF NOT EXISTS FOR (cn:Country) REQUIRE cn.id IS UNIQUE;
CREATE CONSTRAINT country_name IF NOT EXISTS FOR (cn:Country) REQUIRE cn.name IS UNIQUE;
CREATE CONSTRAINT chokepoint_id IF NOT EXISTS FOR (cp:Chokepoint) REQUIRE cp.id IS UNIQUE;
CREATE CONSTRAINT chokepoint_name IF NOT EXISTS FOR (cp:Chokepoint) REQUIRE cp.name IS UNIQUE;
CREATE CONSTRAINT newsitem_id IF NOT EXISTS FOR (n:NewsItem) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT newsitem_url IF NOT EXISTS FOR (n:NewsItem) REQUIRE n.url IS UNIQUE;

// ---- nodes: one pass per label over the same file ----
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS row
WITH row WHERE row.label = "Company"
MERGE (c:Company {id: row.id})
SET c.name = row.name,
    c.ticker = row.ticker,
    c.exchange = row.exchange,
    c.country = row.country,
    c.layer = row.layer,
    c.sub_segment = row.sub_segment,
    c.tier = toInteger(row.tier),
    c.chokepoint = (row.chokepoint = "true"),
    c.description = row.description,
    c.key_products = split(row.key_products, "|"),
    c.key_customers = split(row.key_customers, "|"),
    c.fab_or_ops_geography = split(row.fab_or_ops_geography, "|"),
    c.source = row.source;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS row
WITH row WHERE row.label = "Layer"
MERGE (l:Layer {id: row.id})
SET l.name = row.name, l.order = toInteger(row.order);

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS row
WITH row WHERE row.label = "Technology"
MERGE (t:Technology {id: row.id})
SET t.name = row.name;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS row
WITH row WHERE row.label = "Country"
MERGE (cn:Country {id: row.id})
SET cn.name = row.name, cn.code = row.code;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS row
WITH row WHERE row.label = "Chokepoint"
MERGE (cp:Chokepoint {id: row.id})
SET cp.name = row.name, cp.layer = row.layer;

// ---- edges: one pass per relationship type, matched on id ----
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/edges.csv") AS row
WITH row WHERE row.type = "OPERATES_IN"
MATCH (a:Company {id: row.from_id}), (b:Layer {id: row.to_id})
MERGE (a)-[r:OPERATES_IN]->(b)
SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/edges.csv") AS row
WITH row WHERE row.type = "HQ_IN"
MATCH (a:Company {id: row.from_id}), (b:Country {id: row.to_id})
MERGE (a)-[r:HQ_IN]->(b)
SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/edges.csv") AS row
WITH row WHERE row.type = "CONTROLS"
MATCH (a:Company {id: row.from_id}), (b:Chokepoint {id: row.to_id})
MERGE (a)-[r:CONTROLS]->(b)
SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/edges.csv") AS row
WITH row WHERE row.type = "DEPENDS_ON"
MATCH (a:Company {id: row.from_id}), (b:Technology {id: row.to_id})
MERGE (a)-[r:DEPENDS_ON]->(b)
SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/edges.csv") AS row
WITH row WHERE row.type = "SUPPLIES"
MATCH (a:Company {id: row.from_id}), (b:Company {id: row.to_id})
MERGE (a)-[r:SUPPLIES]->(b)
SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/edges.csv") AS row
WITH row WHERE row.type = "COMPETES_WITH"
MATCH (a:Company {id: row.from_id}), (b:Company {id: row.to_id})
MERGE (a)-[r:COMPETES_WITH]->(b)
SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence;

// ---- check: should print 216 nodes and 869 edges ----
MATCH (n) WITH count(n) AS nodes
MATCH ()-[r]->() RETURN nodes, count(r) AS edges;

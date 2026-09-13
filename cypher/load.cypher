// chip-kg loader — paste this whole file into Neo4j Browser (Aura) and run it.
// Safe to re-run: everything uses MERGE, never CREATE.
//
// Replace <RAW_BASE> below with the raw GitHub URL for this repo's main
// branch, e.g. https://raw.githubusercontent.com/<your-username>/chip-kg/main
:param raw_base => "<RAW_BASE>";

// ---- constraints ----
CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT layer_name IF NOT EXISTS FOR (l:Layer) REQUIRE l.name IS UNIQUE;
CREATE CONSTRAINT technology_name IF NOT EXISTS FOR (t:Technology) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT country_name IF NOT EXISTS FOR (co:Country) REQUIRE co.name IS UNIQUE;
CREATE CONSTRAINT chokepoint_name IF NOT EXISTS FOR (ch:Chokepoint) REQUIRE ch.name IS UNIQUE;

// ---- nodes: one LOAD CSV pass per label, filtered from the same file ----
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS row
WITH row WHERE row.label = "Company"
MERGE (c:Company {name: row.name})
SET c.ticker = row.ticker,
    c.exchange = row.exchange,
    c.listed = (row.listed = "true"),
    c.tier = toInteger(row.tier);

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS row
WITH row WHERE row.label = "Layer"
MERGE (l:Layer {name: row.name})
SET l.order = toInteger(row.order);

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS row
WITH row WHERE row.label = "Technology"
MERGE (t:Technology {name: row.name});

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS row
WITH row WHERE row.label = "Country"
MERGE (co:Country {name: row.name})
SET co.code = row.code;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS row
WITH row WHERE row.label = "Chokepoint"
MERGE (ch:Chokepoint {name: row.name})
SET ch.layer = row.layer;

// ---- edges: one LOAD CSV pass per relationship type ----
// id_to_name lookups happen by joining edges.csv back to nodes.csv on id,
// since edges reference node ids but the graph is keyed on name.

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/edges.csv") AS row
WITH row WHERE row.type = "OPERATES_IN"
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS fn
WITH row, fn WHERE fn.id = row.from_id
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS tn
WITH row, fn, tn WHERE tn.id = row.to_id
MATCH (a:Company {name: fn.name})
MATCH (b:Layer {name: tn.name})
MERGE (a)-[r:OPERATES_IN]->(b)
SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/edges.csv") AS row
WITH row WHERE row.type = "HQ_IN"
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS fn
WITH row, fn WHERE fn.id = row.from_id
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS tn
WITH row, fn, tn WHERE tn.id = row.to_id
MATCH (a:Company {name: fn.name})
MATCH (b:Country {name: tn.name})
MERGE (a)-[r:HQ_IN]->(b)
SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/edges.csv") AS row
WITH row WHERE row.type = "CONTROLS"
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS fn
WITH row, fn WHERE fn.id = row.from_id
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS tn
WITH row, fn, tn WHERE tn.id = row.to_id
MATCH (a:Company {name: fn.name})
MATCH (b:Chokepoint {name: tn.name})
MERGE (a)-[r:CONTROLS]->(b)
SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/edges.csv") AS row
WITH row WHERE row.type = "DEPENDS_ON"
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS fn
WITH row, fn WHERE fn.id = row.from_id
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS tn
WITH row, fn, tn WHERE tn.id = row.to_id
MATCH (a:Company {name: fn.name})
MATCH (b:Technology {name: tn.name})
MERGE (a)-[r:DEPENDS_ON]->(b)
SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/edges.csv") AS row
WITH row WHERE row.type = "SUPPLIES"
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS fn
WITH row, fn WHERE fn.id = row.from_id
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS tn
WITH row, fn, tn WHERE tn.id = row.to_id
MATCH (a:Company {name: fn.name})
MATCH (b:Company {name: tn.name})
MERGE (a)-[r:SUPPLIES]->(b)
SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence;

LOAD CSV WITH HEADERS FROM ($raw_base + "/data/edges.csv") AS row
WITH row WHERE row.type = "COMPETES_WITH"
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS fn
WITH row, fn WHERE fn.id = row.from_id
LOAD CSV WITH HEADERS FROM ($raw_base + "/data/nodes.csv") AS tn
WITH row, fn, tn WHERE tn.id = row.to_id
MATCH (a:Company {name: fn.name})
MATCH (b:Company {name: tn.name})
MERGE (a)-[r:COMPETES_WITH]->(b)
SET r.as_of = row.as_of, r.source = row.source, r.confidence = row.confidence;

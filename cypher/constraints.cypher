// chip-kg constraints. Paste into Neo4j Browser (Aura) and run.
// Safe to re-run: every statement uses IF NOT EXISTS.
//
// Every node has a unique id (prefixed co: ly: te: cn: cp: nw:).
// Names are unique within each label. NewsItem is unique on url.

CREATE CONSTRAINT company_id IF NOT EXISTS
FOR (c:Company) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT company_name IF NOT EXISTS
FOR (c:Company) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT layer_id IF NOT EXISTS
FOR (l:Layer) REQUIRE l.id IS UNIQUE;

CREATE CONSTRAINT layer_name IF NOT EXISTS
FOR (l:Layer) REQUIRE l.name IS UNIQUE;

CREATE CONSTRAINT technology_id IF NOT EXISTS
FOR (t:Technology) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT technology_name IF NOT EXISTS
FOR (t:Technology) REQUIRE t.name IS UNIQUE;

CREATE CONSTRAINT country_id IF NOT EXISTS
FOR (cn:Country) REQUIRE cn.id IS UNIQUE;

CREATE CONSTRAINT country_name IF NOT EXISTS
FOR (cn:Country) REQUIRE cn.name IS UNIQUE;

CREATE CONSTRAINT chokepoint_id IF NOT EXISTS
FOR (cp:Chokepoint) REQUIRE cp.id IS UNIQUE;

CREATE CONSTRAINT chokepoint_name IF NOT EXISTS
FOR (cp:Chokepoint) REQUIRE cp.name IS UNIQUE;

CREATE CONSTRAINT newsitem_id IF NOT EXISTS
FOR (n:NewsItem) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT newsitem_url IF NOT EXISTS
FOR (n:NewsItem) REQUIRE n.url IS UNIQUE;

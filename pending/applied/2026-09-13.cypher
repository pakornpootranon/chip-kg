// Proposed update — 2026-09-13
// Source: https://app.bigdata.com/documents/675F51496F8D503911CF021D02B17E8A
// Add-only: every statement below is MATCH existing nodes + MERGE a NEW
// relationship carrying this as_of. Nothing here can DELETE or modify an
// existing edge's properties — that's enforced by propose_updates.py, not
// just a convention.
//
// Diff (plain English):
//   SUPPLIES: ASML -> TSMC (confidence: medium) — TSMC becomes ASML's 2nd High-NA EUV customer after Intel; will begin using High-NA systems with 6-inch masks in 2030, full 12-inch mass production targeted 2033. CEO C.C. Wei quoted directly announcing the agreement.
//   SUPPLIES: ASML -> Samsung Electronics (confidence: medium) — Samsung becomes ASML's 3rd High-NA EUV customer after Intel, plans to use High-NA tools for memory production by 2028; expanded existing ASML partnership announced by Samsung's Vice Chairman/CEO.

MATCH (a:Company {name: "ASML"}), (b:Company {name: "TSMC"})
MERGE (a)-[:SUPPLIES {as_of: "2026-09-13", source: "https://app.bigdata.com/documents/675F51496F8D503911CF021D02B17E8A", confidence: "medium"}]->(b);

MATCH (a:Company {name: "ASML"}), (b:Company {name: "Samsung Electronics"})
MERGE (a)-[:SUPPLIES {as_of: "2026-09-13", source: "https://app.bigdata.com/documents/675F51496F8D503911CF021D02B17E8A", confidence: "medium"}]->(b);

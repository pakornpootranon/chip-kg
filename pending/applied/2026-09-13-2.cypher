// Proposed update 2026-09-13
// Source: https://app.bigdata.com/documents/A5D30993895106F2EDB7BFCBE25A4AF0
// Add-only: each statement matches existing nodes and merges a NEW relationship
// with this as_of. Existing edges are never changed or removed.
//
// Diff:
//   SUPPLIES: Arm Holdings -> Samsung Electronics (confidence: low) | Arm supplies AI accelerator architecture + RTL design IP for a joint 2nm on-device AI SoC; Samsung System LSI integrates, Samsung Foundry manufactures on SF2. NRE fees approved end of Aug 2026, reported early Sep 2026.

MATCH (a:Company {name: "Arm Holdings"}), (b:Company {name: "Samsung Electronics"})
MERGE (a)-[:SUPPLIES {as_of: "2026-09-13", source: "https://app.bigdata.com/documents/A5D30993895106F2EDB7BFCBE25A4AF0", confidence: "low"}]->(b);

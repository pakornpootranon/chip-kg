// SCREEN 01: Single-source chokepoints
//
// What it finds: every Chokepoint that exactly one Company CONTROLS.
// These are the tightest bottlenecks in the chip supply chain: no second
// supplier exists in the graph at all.
//
// Why an investor cares: single-source control usually means pricing power
// and a wide moat. It also means concentrated risk. If the one company slips
// (execution, export controls, a plant offline) there is no graphed backup.
//
// What a hit does not mean: it does not prove the company has zero
// competitors in the real world, only that this graph has no other Company
// controlling the same Chokepoint. Read data/GAPS.md for the judgment calls
// behind each CONTROLS edge, and check the edge's confidence.
//
// Variation: change "n = 1" to "n <= 2" to see duopolies as well.

MATCH (c:Company)-[r:CONTROLS]->(cp:Chokepoint)
WITH cp, collect(c.name) AS controllers, collect(r.confidence) AS confidence, count(c) AS n
WHERE n = 1
RETURN cp.name AS chokepoint, cp.layer AS layer, controllers[0] AS controlled_by, confidence[0] AS confidence
ORDER BY layer, chokepoint;

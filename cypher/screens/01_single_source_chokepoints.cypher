// SCREEN: Single-source chokepoints
//
// What it finds: every Chokepoint in the graph that is CONTROLS-ed by
// exactly one Company. These are the tightest bottlenecks in the chip
// supply chain — no second supplier exists in this graph at all.
//
// Why an investor cares: single-source control usually means pricing
// power and a wide moat. If the controlling company slips (execution,
// export controls, a plant going offline), there is no graphed backup —
// that's a concentrated risk as well as a concentrated opportunity.
//
// What a hit does NOT mean: it doesn't mean the company has zero real-world
// competitors — only that this graph doesn't (yet) have another Company
// CONTROLS-ing the same Chokepoint. Check data/GAPS.md; some chokepoints
// (Silicon Wafers, Photoresist) have no CONTROLS edge at all yet because
// the source material only gave a country-level split, not a per-company
// one — those won't show up here even though they're concentrated in
// reality.

MATCH (c:Company)-[:CONTROLS]->(ch:Chokepoint)
WITH ch, collect(c.name) AS controllers, count(c) AS n
WHERE n = 1
RETURN ch.name AS chokepoint, controllers[0] AS controlled_by
ORDER BY chokepoint;

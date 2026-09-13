// SCREEN: Stale edges
//
// What it finds: every relationship whose `as_of` date is older than
// $months months, oldest first.
//
// Why an investor cares: this graph is only useful if its relationships
// stay current. A stale edge is a prompt to re-check whether a supply
// relationship, competitive dynamic, or chokepoint control still holds —
// the chip industry moves fast enough that a two-year-old "controls" claim
// can quietly go stale.
//
// What a hit does NOT mean: a stale edge is not automatically wrong — per
// CLAUDE.md's data rules, automated update flows never DELETE or SET on an
// existing edge, so staleness is surfaced here for a human to review, not
// auto-corrected. Confirm before relying on an old edge for a decision.
//
// Usage: set $months to the staleness threshold, e.g. 6.
:param months => 6;

MATCH (a)-[r]->(b)
WHERE date(r.as_of) < date() - duration({months: $months})
RETURN type(r) AS relationship, a.name AS from_company, b.name AS to_node,
       r.as_of AS as_of, r.source AS source, r.confidence AS confidence
ORDER BY r.as_of ASC;

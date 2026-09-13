// SCREEN 05: Stale edges
//
// What it finds: every relationship whose as_of date is older than $months
// months, oldest first, with its source and confidence.
//
// Why an investor cares: the graph is only useful while its relationships
// are current. The chip industry moves fast enough that a two-year-old
// "controls" or "supplies" claim can quietly stop being true.
//
// What a hit does not mean: stale is not wrong. Nothing in this graph is
// deleted or overwritten by an automated job; staleness is surfaced here for
// a person to re-check. Edges with source "claude-knowledge" all carry the
// same as_of date (the day the graph was built), so they will appear as one
// block when they age past the threshold. The right fix for one you have
// verified is to replace the source with a URL and bump as_of.
//
// Usage: set $months to the threshold, e.g. 6.
:param months => 6;

MATCH (a)-[r]->(b)
WHERE r.as_of IS NOT NULL AND date(r.as_of) < date() - duration({months: $months})
RETURN type(r) AS relationship, a.name AS from_node, b.name AS to_node,
       r.as_of AS as_of, r.source AS source, r.confidence AS confidence
ORDER BY r.as_of ASC, relationship, from_node;

# Screens

Five starter queries for the chip-kg graph. Paste any of them into Neo4j
Browser (they're plain Cypher, no client needed) or ask Claude to run them
for you via the Neo4j MCP connection.

## 1. Single-source chokepoints

Finds every chokepoint in the chip supply chain that this graph shows only
one company controlling: right now that's ASML on EUV lithography, TSMC on
advanced (sub-7nm) foundry capacity, and SK Hynix on HBM memory. These are
the tightest bottlenecks the graph knows about. A hit here is a strong
signal, but it only reflects what's been added to the graph so far. Some
real chokepoints, like Japan's grip on silicon wafers and photoresist, don't
show up yet because the source material only gave a country-level split,
not a named company.

## 2. Upstream of a company

Given a company name, this walks up to two SUPPLIES hops backward to find
every listed company that feeds into it, grouped by which layer of the
supply chain they sit in. Point it at NVIDIA and you get TSMC (foundry),
Micron (IDM), and SK Hynix (memory) today. This is the core relationship
screen the graph exists for: it finds exposure to a company's growth
without touching a single financial ratio. The result only grows as more
SUPPLIES edges get added, so a short list today doesn't mean a company has
few real suppliers, only that fewer have been mapped so far.

## 3. Country concentration by layer

For every layer of the chip supply chain, shows what share of the companies
in it are headquartered in each country. Materials is 100% Japan in this
graph; Equipment is majority US with single names from the Netherlands,
Japan, and Germany. This is the fastest way to see where a regional shock,
whether a natural disaster or an export ban, would hit hardest. It only
measures where a company is headquartered, not where it actually
manufactures, so read it alongside the SUPPLIES edges for the fuller
picture.

## 4. Tier 2 companies feeding Tier 1

Ranks Tier 2 companies (critical suppliers with a handful of credible
competitors) by how many SUPPLIES relationships they have running into
Tier 1 companies (the names that control a chokepoint outright). The idea:
riding a Tier 1 name's pricing power through its Tier 2 supplier can be a
less crowded, lower-concentration-risk way to play the same theme. The
graph currently only has one such edge (Micron into NVIDIA), which says more
about how young this graph is than about the real world. Expect this list
to grow as more supplier relationships get added.

## 5. Stale edges

Takes a number of months and lists every relationship older than that,
oldest first. Nothing in this graph gets deleted or silently corrected;
per the data rules in CLAUDE.md, an automated update can only add a new
edge with a fresh date, never erase or overwrite an old one. This screen is
how a stale claim gets surfaced for a human to check, rather than trusted
forever just because it's still sitting in the graph.

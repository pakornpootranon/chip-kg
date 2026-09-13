# Screens and analysis prompts

Two ways to ask the graph questions. **Screens** are plain Cypher files in `cypher/screens/`; paste one into the Query editor, or ask Claude to run it. **Analysis prompts** are text files in `prompts/analysis/`; paste one into Claude Desktop with the chip-kg connector on ([`mcp.md`](mcp.md)) and Claude writes the Cypher itself. Every screen file opens with a comment saying what it finds, why an investor cares, and what a hit does and does not mean.

## Screens

### 01 Single-source chokepoints

Lists every chokepoint that exactly one company controls. Today that is ASML on EUV lithography, Lasertec on EUV mask inspection and Ajinomoto on ABF substrate film. These are the tightest bottlenecks the graph knows about, which means pricing power and concentrated risk at once. Advanced foundry and HBM do not appear because Samsung and Micron are recorded as second controllers at medium confidence. Change the `n = 1` to `n <= 2` to see duopolies too.

### 02 Upstream of a company

Give it a company name (change `"NVIDIA"` on the `:param company_name` line at the top of the file) and it walks up to two SUPPLIES hops backwards, grouping the suppliers by layer and showing each one's tier. Pointed at NVIDIA it returns fifty-three companies across nine layers, from TSMC and the memory makers one hop out to the wafer, gas and subsystem suppliers two hops out. This is the core relationship screen the graph exists for. Distance says nothing about revenue materiality, so treat it as a list of names to research, not a ranking.

### 03 Country concentration by layer

For each layer, the share of companies headquartered in each country. Packaging is 62 percent Taiwan and Materials 43 percent Japan by count. It measures where companies are domiciled, not where the plants are; a US fabless company builds everything in Taiwan. Read it next to the `fab_or_ops_geography` list on each company.

### 04 Tier 2 feeding Tier 1

Ranks Tier 2 companies by how many Tier 1 chokepoint controllers they supply. Advantest leads with three (TSMC, SK Hynix, NVIDIA), then Lam Research, SUMCO and Shin-Etsu with two each. The idea is to ride Tier 1 pricing power through a supplier that does not carry the same single-source risk. Tier is a judgment call recorded in `data/universe.csv`.

### 05 Stale edges

Takes a number of months and lists every relationship older than that. The graph never deletes or overwrites; an old claim is surfaced here for a person to re-check. Most edges in v2 carry the same build date and source `claude-knowledge`, so when they cross the threshold they arrive as one block. The fix for a verified edge is a URL in `source` and a new `as_of`.

### 06 News heat

Ranks companies by how many NewsItem nodes mention them in the last N days, split into positive, negative and neutral, with the chokepoints and technologies those items affect. Ordered so chokepoint controllers and Tier 1 names come first. Empty until the daily task ([`schedule.md`](schedule.md)) has run. Counts measure attention, not importance; open the linked items before acting.

## Analysis prompts

### Which of my holdings share a chokepoint?

You list your chip holdings. Claude finds each one, then checks every pair for a shared chokepoint (both control it, or one controls it and the other sits within two supply hops), or a shared technology dependency. The output is a table of connected pairs and a short note on which single chokepoint your portfolio leans on most. Use it to see whether five stocks are really five bets or one.

### What breaks if X stops shipping?

Name a company and Claude walks downstream: direct customers, their customers, the chokepoints and technologies involved, and the competitors that could substitute. It ends with an eight-line brief and an honest note on where the graph is thin. Try it on ASML, then on a Tier 3 name, to feel the difference between a chokepoint and a commodity supplier.

### Compare two names on the graph

Two companies, one table: layer, tier, geography, who they supply, who supplies them, chokepoints, technologies, competitors, shared and unique customers. Then a few sentences on where their positions differ. Works best for two names in the same layer, such as Lam Research and Tokyo Electron; Claude will say so if they are not.

### What changed this week?

Reads the last seven days of NewsItem nodes and writes a ranked brief: chokepoint hits first, then Tier 1, Tier 2, Tier 3. It ends with one line on which graph relationships the news suggests may have changed, so you can decide whether to edit the CSVs. Read-only; it never touches the graph. Needs the daily task to have run.

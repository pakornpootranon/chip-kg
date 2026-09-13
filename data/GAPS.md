# Gaps and judgment calls — Task 2 (v1, from Chip War Essential Guide only)

## 1. Node count is well short of the 150+ target
The guide is a curated investor digest, not a company directory. It names
about 44 distinct companies with enough detail to seed a node. Total graph:
44 Companies + 10 Layers + 7 Countries + 6 Technologies + 7 Chokepoints = 74
nodes. Hitting 150+ from this source alone would mean inventing companies or
relationships it doesn't state — against the "do not scrape third-party
sites to fill gaps" rule. Options: (a) accept ~74 as the v1 graph and grow it
edge-by-edge in Post 2 via `propose_updates.py` / real news, per the series'
existing add-only pattern; (b) approve a second source document (the
Quantum_Race or Rare_Earths essential guides also sit in Downloads, but
CLAUDE.md names only the Chip War guide as source — needs your sign-off to
add another); (c) raise the target's expectation in CLAUDE.md/PLAN.md. Not
decided — needs your call before Task 3.

## 2. IP layer has zero companies
The guide never discusses chip IP licensing (e.g. Arm, Synopsys DesignWare,
CEVA) — it's outside its memory/storage-investor scope. The `IP` layer
exists in the ontology but is currently empty. Flagging rather than
inventing a company for it.

## 3. Tickers and exchanges are not in the guide
The guide states tickers only for the four portfolio names (MU, STX, WDC,
PSTG). Every other ticker/exchange in `nodes.csv` (ASML, TSM, NVDA, INTC,
etc.) came from my own general knowledge of public identifiers, not from the
guide text. This felt different from fabricating a *relationship* claim —
tickers are stable public facts, not judgment calls — but it's a deviation
from "the guide is the source" as literally written, so flagging it
explicitly. A few are lower-confidence and should be double-checked before
publishing:
- **JSR Corporation** (`c_jsr`) — I believe JSR went private in 2024 via a
  JIC-backed tender offer and may no longer trade as 4185.T. Marked
  `listed: true` provisionally; verify before use.
- **Kioxia** (`c_kioxia`) — IPO'd on TSE in December 2024; ticker `285A.T`
  is from memory, not independently verified here.
- **ASE Technology** (`c_ase`) — used the NYSE ADR ticker `ASX`; it also
  trades as `3711.TW` in Taiwan. Pick one convention if this matters for
  screening.
- **Siemens (Mentor)** (`c_siemens_mentor`) — Mentor Graphics was fully
  absorbed into Siemens EDA and isn't separately listed; the ticker/exchange
  here (`SIE.DE`) is the *parent* Siemens AG, which is a much bigger, more
  diversified company than the EDA unit alone. Treat this node as "Siemens'
  EDA business," not a pure-play.

## 4. Layer assignment for multi-role companies (exactly-one OPERATES_IN)
The ontology requires each Company to have exactly one `OPERATES_IN`, but
several real companies span layers. Judgment calls made:
- **Samsung, Intel, Micron, Texas Instruments, Infineon, Sony, onsemi,
  Cirrus Logic → IDM** (they design and manufacture their own chips), even
  though Samsung and Micron are usually thought of primarily as "Memory" and
  Intel as "Foundry" in casual usage.
- **Western Digital, Seagate, Pure Storage → EndDemand** (storage systems
  companies that consume/integrate memory chips, rather than fabricating a
  chip themselves). This stretches "EndDemand" to mean device/system makers,
  not literal end consumers — confirm that's the intended reading.
- **Apple → Fabless** (its chip-design arm), even though Apple's real
  business is devices, not chip sales.

## 5. Tier assignments are the shakiest calls in the file
CLAUDE.md's tier rule ("controls a chokepoint with 1-2 / 3-5 competitors")
fits upstream layers (Equipment, Materials, Foundry, EDA, Memory) cleanly
but doesn't map obviously onto Fabless/EndDemand companies, whose moat is a
different kind (ecosystem lock-in, brand, scale) rather than supply
chokepoint control. Calls that most need your review:
- NVIDIA → Tier 1 on CUDA/AI-GPU ecosystem lock-in, not a classic chokepoint.
- WDC and Seagate → Tier 1 on HDD duopoly concentration, even though
  EndDemand isn't really a "picks-and-shovels" layer.
- Zeiss and Cymer → Tier 1 as ASML's sole named optics/laser suppliers, but
  the guide never gives them individual chokepoint status the way it does
  ASML/TSMC/Cadence-Synopsys/SK Hynix.
- Applied Materials, Lam Research, KLA, Tokyo Electron → Tier 2, despite
  each holding 25-55% of a specific equipment sub-step, because the guide's
  formal Chokepoint table only names EUV, not deposition/etch/inspection
  individually.
- Texas Instruments → Tier 2, despite the guide calling it "the dominant
  player" in analog (10.4), because the same section frames analog overall
  as "more distributed" (i.e. not a chokepoint).
- SMIC → Tier 3 despite strategic importance to China's self-sufficiency
  push, because globally it remains sanctions-limited and trailing-edge.

## 6. CONTROLS edges skipped for split chokepoints
Silicon Wafers (Shin-Etsu + SUMCO, "Japan: 75%") and Photoresist (JSR + TOK +
Shin-Etsu, "Japan: 90%+") are given as country-level shares in the guide,
without a per-company split. Rather than guess an individual company's
share, I left these two Chokepoint nodes without a `CONTROLS` edge. They
still exist as nodes (referenced by the Materials layer) — add the edges
once you have (or want to assert) a company-level split.

## 7. Ownership relationships not modeled
Real-world ASML holds a minority stake in Zeiss SMT, and Cymer has been a
wholly-owned ASML subsidiary since 2013 — neither fact is stated in this
guide, and the ontology has no "owns/subsidiary-of" relationship type
anyway. Both are modeled here as independent Companies with a plain
`SUPPLIES` edge into ASML, which understates how integrated they actually
are. Flagging in case that matters for the tier-1 chokepoint framing.

## 8. DRAM / NAND / NOR Flash Technology nodes are unconnected
Created per the ontology's Technology label, but no company has an explicit
`DEPENDS_ON` edge to them yet — the guide describes who *makes* these
(that's the Memory/IDM layer), not who structurally depends on them the way
GPUs explicitly depend on HBM. Leaving them node-only until a real
dependency claim is sourced.

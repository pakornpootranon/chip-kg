# Gaps and judgment calls

## Task 2 notes (2026-09-13): universe.csv, for Pootranon's review

Dropped from v1 because they are not listed: Zeiss SMT (Carl Zeiss AG is private), Cymer (ASML subsidiary), JSR (taken private by JIC in 2024), YMTC, Huawei/HiSilicon, Imagination Technologies, SiFive. Their supply relationships can still appear in descriptions but they get no node.

Not added although relevant, because not listed or no longer listed: CXMT (private, Bigdata.com confirms), SK Siltron (private), Shinko Electric (taken private 2025), Ansys (bought by Synopsys 2025), Alphawave (bought by Qualcomm 2025), Toshiba (delisted 2023).

Tickers moved from US ADRs to the primary local listing, per the CLAUDE.md ticker rule: TSMC 2330.TW (was TSM), ASE 3711.TW (was ASX), UMC 2303.TW (was UMC), Sony 6758.T (was SONY), STMicro STMPA.PA (was STM). ASML stays bare per the CLAUDE.md example. Himax and Silicon Motion keep their NASDAQ tickers because they have no local listing.

Layer changes from v1: Micron moved IDM to Memory. Cirrus Logic moved IDM to Fabless (it owns no fabs). Silicon Labs, Silicon Motion, Phison and Montage are Fabless (chip designers) even though two of them sell memory controllers. Photronics, HOYA and AGC sit in Materials (photomasks and mask blanks). Ibiden and Unimicron sit in Packaging (IC substrates).

Country judgment calls: STMicro CH (Geneva head office; incorporated in NL). Silergy CN (Hangzhou operations; Cayman incorporated, Taiwan listed). Kulicke & Soffa SG (Singapore head office; US incorporated). Linde IE (Irish incorporation; UK head office). X-FAB BE. Wingtech CN (parent of Nexperia, whose control is disputed with the Dutch government since late 2025).

Tier calls that need a look: Lasertec Tier 1 with chokepoint true (sole supplier of actinic EUV mask inspection). HOYA Tier 1 with chokepoint true and Ajinomoto Tier 1 with chokepoint true (EUV mask blanks duopoly with AGC; ABF substrate film near-monopoly). DISCO Tier 1, chokepoint false (about 80 percent of dicing and grinding, but Tier 1 by the one-or-two-competitors rule). Western Digital and Seagate keep v1's Tier 1 but that looks generous for a three-player hard-drive market; Tier 2 may fit better. Hanmi Semiconductor Tier 2 (HBM thermal-compression bonders). Every hyperscaler and server maker in EndDemand is Tier 3 by default, as in v1.

Vanguard International Semiconductor 5347.TWO could not be resolved by Bigdata.com find_securities; the ticker is from knowledge and should be checked once in Aura or Yahoo.

The universe is 171 names. That is larger than the 100 minimum on purpose; trim in the review if the Task 3 enrichment load (batches of 20 per session) is too heavy.

## v5 (2026-09-13): Hermes path dropped

The Hermes follower path described in v4 below was abandoned the same day and
its files removed from the repo. History kept here for the record only. The
update loop is now a Claude scheduled task writing NewsItem nodes; see PLAN.md.

## v4 (2026-09-13): follower path rebuilt after a validation pass

What was wrong for a follower, all found by checking against a live Hermes
install rather than the plan text: three commits were unpushed while
`load.cypher` reads raw GitHub `main` (a follower would have loaded the old
74-node graph); the README's "point Hermes at the file / enter credentials
when prompted" instructions did not work (YAML editing, a category-folder
quirk, a desktop-sandbox symlink quirk, and Telegram/cron surfaces cannot
prompt for secrets); the scripts required a git clone; and credentials used
two different variable names. All fixed; see PLAN.md's Task 7 note. Still
open: the Hermes + Telegram round trip has now been tested up to the install
and script execution on the author's machine, but not the scheduled
Telegram delivery and approval reply, which needs a real Monday (or an
on-demand message from Telegram).

## v3 (2026-09-13): Task 7 update-loop scripts, tested live

`scripts/propose_updates.py` and `scripts/apply_updates.py` were tested end
to end against the real live Aura instance using two genuine, dated news
items (found via Bigdata.com search, not invented): Arm Holdings supplying
AI accelerator IP for a joint Samsung 2nm SoC (Sep 4 2026), and ASML
confirming TSMC and Samsung as its 2nd/3rd High-NA EUV customers (Sep 9
2026). Both are now real edges in the graph with `source` set to the actual
article URL — not test data to be cleaned up later.

**One real bug found by this testing, now fixed:** `apply_updates.py`
originally archived a file to `pending/applied/<same name>`, so a second
same-day apply would silently overwrite the first one's archive entry (no
graph or `edges.csv` data was lost — those are keyed correctly — but the
local audit trail would have been). Fixed to number duplicates instead
(`<name>-2.cypher`, etc.).

**Local environment note, not a repo bug:** this machine's network does TLS
interception on port 7687 (a self-signed cert shows up where Aura's real
cert should be — almost certainly corporate security software, not
anything wrong with Aura). Direct `neo4j+s://` connections from a local
Python script fail with `CERTIFICATE_VERIFY_FAILED` here, even though the
MCP server connection works fine (it likely runs in an isolated environment
with its own trust handling). Worked around locally with `neo4j+ssc://`
(same encryption, skips full chain verification) — **do not put this in
the public docs as the default**, since it weakens security for anyone on a
normal network. If the author hits the same error running these scripts
locally, that's the fix to try, but `neo4j+s://` should stay the documented
default in `.env.example`/README.

**Not tested: the actual Hermes + Telegram round trip.** No live Hermes
account was available in this session. `skills/kg-update/SKILL.md` and the
README's cron instructions are written against Hermes's real documented
skill/cron format (verified live via its docs, not guessed), but "the diff
arrived on Telegram and a human approved it in that chat" specifically
needs a real Hermes instance to confirm. Worth a real run before calling
Task 7 fully closed.

## v2 (2026-09-13): expanded via Bigdata.com beyond the Essential Guide

Author approved a second source for this round: the Bigdata.com company/
security data connected in this session, used to (a) verify every ticker
below flagged as shaky in v1 and (b) add 49 companies + 3 countries the
guide never names, concentrated in layers the guide barely touches (IP went
from 0 to 7 companies; every layer now has 5+). This is a real change to
CLAUDE.md's "Chip War Essential Guide is the source" rule, done with
sign-off, not silently.

**How the two sources are distinguished in the data:** every guide-sourced
edge keeps `source: essential-guide`, `as_of: 2026-04-01`. Every
Bigdata-sourced edge added this round uses `source: "bigdata.com company
profile"` (for OPERATES_IN/HQ_IN — objective, verified facts) or `source:
"bigdata.com / industry knowledge"` (for SUPPLIES/COMPETES_WITH/DEPENDS_ON —
well-known industry relationships I did not pull a specific filing citation
for), `as_of: 2026-09-13`, confidence `medium` throughout (never `high`,
since none of these have a specific filing/earnings-call citation behind
them yet). **Treat every "bigdata.com / industry knowledge" edge as a TODO
to backfill with a real source** before leaning on it for a public claim —
same spirit as the 7 pre-existing `source: TODO` edges in the old vault
version of this project.

New totals: 126 nodes (93 Companies, 10 Layers, 10 Countries, 6
Technologies, 7 Chokepoints), 264 edges. `validate.py` exits 0. Live Aura
counts reconfirmed via MCP: 126 nodes / 264 edges, matching exactly.

**Verification caught two real, useful corrections** (worth knowing for
Post 2/3 "what the graph got wrong" content):
- **JSR Corporation** — v1 flagged suspicion it had gone private in 2024.
  Confirmed via Bigdata: acquired by Japan Investment Corporation (JICC-02)
  April 2024, delisted from TSE October 2024. Node corrected: `listed:
  false`, ticker/exchange cleared. The guide-sourced OPERATES_IN/HQ_IN/
  CONTROLS facts about JSR (Materials, Japan, photoresist) are unaffected.
- **Two real Stage-5-Materials CONTROLS edges were missing from v1**: the
  guide's own table names Shin-Etsu+SUMCO for Silicon Wafers and
  Shin-Etsu+JSR+TOK for Photoresist (docx lines ~340-352), but v1 never
  turned that into CONTROLS edges (see old item 6 below, now resolved for
  the guide-sourced companies). Added as `essential-guide`/`high`. Also
  added GlobalWafers → Silicon Wafers at `bigdata.com`/`medium` since it's
  a real top-3 global wafer maker not mentioned in the guide.

**Dropped candidates, in case worth a second try:**
- **Alphawave IP Group** (would have been an IP-layer add) — Qualcomm
  acquired it in December 2025 and it delisted from the LSE (continues
  trading OTC as AWEVF). Excluded rather than added with an ambiguous
  "independent public company" status; the acquisition itself is good real
  material for a future Post 2 "real news → edge diff" demo.
- **Vanguard International Semiconductor (VIS)** and **Will Semiconductor**
  (Shanghai, image sensors) — considered for Foundry/Fabless respectively
  but `find_securities` didn't resolve them under the query terms tried this
  session. Worth retrying with a ticker-based lookup (VIS trades as 5347 on
  TPEx; Will Semiconductor as 603501.SS) rather than name search.
- Renesas Electronics was originally NEC Electronics's chip business, and
  Tongfu Microelectronics was originally "Nantong Fujitsu Microelectronics"
  — a nice historical echo of the guide's Ch.6 Japan-DRAM-era names (NEC,
  Fujitsu), but the ontology has no acquired-by/formerly-part-of
  relationship type to capture it. Ask before adding one if this matters for
  Post 2 narrative.
- STMicroelectronics's HQ is genuinely ambiguous (legally incorporated in
  the Netherlands, corporate offices in Geneva, major fabs in France/Italy).
  Used Bigdata's registered-entity country (Netherlands) for consistency
  with how ASML/NXP are already modeled, but flag if you'd rather use
  Geneva/Switzerland.
- The EndDemand layer's 5 new hyperscaler/OEM additions (Microsoft,
  Alphabet, Amazon.com, Meta Platforms, Super Micro Computer) got `tier: 3`
  as a placeholder — see item 5 below, the tier rubric doesn't cleanly apply
  to demand-side companies at all, new or old.

**Original 44-company node count is well short of the abandoned 150+ target,
even now at 93** — the guide names about 44 companies with enough detail to
seed a node; Bigdata verification added the other 49. Going further would
mean either more Bigdata-sourced additions (same medium-confidence pattern)
or another explicit source document. Not pursued further this round; treat
93 companies / 126 nodes as the v2 baseline and keep growing it edge-by-edge
in Post 2 via real news, per the series' existing add-only pattern.

## Original Task 2 gaps (v1, from Chip War Essential Guide only)

## 2. IP layer has zero companies — RESOLVED in v2 above
The guide never discusses chip IP licensing (e.g. Arm, Synopsys DesignWare,
CEVA) — it's outside its memory/storage-investor scope. Filled via Bigdata.com
in the v2 round above (Arm Holdings, CEVA, Rambus, Imagination Technologies,
Andes Technology, VeriSilicon, SiFive — 7 companies).

## 3. Tickers and exchanges are not in the guide
The guide states tickers only for the four portfolio names (MU, STX, WDC,
PSTG). Every other ticker/exchange in `nodes.csv` (ASML, TSM, NVDA, INTC,
etc.) came from my own general knowledge of public identifiers, not from the
guide text. This felt different from fabricating a *relationship* claim —
tickers are stable public facts, not judgment calls — but it's a deviation
from "the guide is the source" as literally written, so flagging it
explicitly. A few are lower-confidence and should be double-checked before
publishing:
- **JSR Corporation** (`c_jsr`) — CONFIRMED in the v2 round above: went
  private in 2024, delisted, node corrected to `listed: false`.
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

## 6. CONTROLS edges skipped for split chokepoints — RESOLVED in v2 above
Silicon Wafers (Shin-Etsu + SUMCO, "Japan: 75%") and Photoresist (JSR + TOK +
Shin-Etsu, "Japan: 90%+") are given as country-level shares in the guide, but
the guide's own Stage 5 table (docx lines ~340-352) does name these specific
companies per material — re-reading it during the v2 round, that's a
per-company list, not a guess. Added as `essential-guide`/`high` CONTROLS
edges. Note this still isn't a *share* split (i.e. we don't know Shin-Etsu's
75% vs SUMCO's remainder) — only that both are named controllers.

## 7. Ownership relationships not modeled
Real-world ASML holds a minority stake in Zeiss SMT, and Cymer has been a
wholly-owned ASML subsidiary since 2013 — neither fact is stated in this
guide, and the ontology has no "owns/subsidiary-of" relationship type
anyway. Both are modeled here as independent Companies with a plain
`SUPPLIES` edge into ASML, which understates how integrated they actually
are. Flagging in case that matters for the tier-1 chokepoint framing.

## 8. DRAM / NAND Technology nodes — partially connected in v2
v1 created these per the ontology's Technology label with no `DEPENDS_ON`
edges (the guide describes who *makes* DRAM/NAND, not who structurally
depends on it the way GPUs explicitly depend on HBM). The v2 round added
three: SanDisk/GigaDevice → NAND, Nanya → DRAM (their whole business
depends on that technology, which is a defensible "depends on" reading).
`NOR Flash` is still unconnected — no company got a NOR-specific edge this
round even though Winbond/Macronix/GigaDevice all make it; add if useful.

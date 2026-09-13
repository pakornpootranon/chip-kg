"""Build data/edges.csv: OPERATES_IN + HQ_IN for every Company, migrated v1 edges,
and new SUPPLIES / COMPETES_WITH / DEPENDS_ON / CONTROLS edges."""
import csv, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TODAY = "2026-09-13"
KNOW = "claude-knowledge"

nodes = {r["id"]: r for r in csv.DictReader(open(ROOT / "data/nodes.csv", encoding="utf-8"))}
name_of = {i: r["name"] for i, r in nodes.items()}
co = {i.split(":", 1)[1]: i for i in nodes if i.startswith("co:")}

# v1 id -> v2 id (None = dropped, unlisted)
V1MAP = {"c_applied_materials": "applied_materials", "c_asm_intl": "asm_international",
         "c_screen_holdings": "screen", "c_ti": "texas_instruments", "c_adi": "analog_devices",
         "c_on_semi": "onsemi", "c_pti": "powertech", "c_siemens_mentor": "siemens",
         "c_wdc": "western_digital", "c_tower_semi": "tower",
         "c_zeiss": None, "c_cymer": None, "c_jsr": None, "c_ymtc": None,
         "c_huawei_hisilicon": None, "c_imagination": None, "c_sifive": None}


def v2id(old):
    if old.startswith("c_"):
        slug = V1MAP.get(old, old[2:])
        return None if slug is None else co[slug]
    if old.startswith("ch_"):
        return "cp:" + old[3:]
    if old.startswith("t_"):
        return "te:" + old[2:]
    raise ValueError(old)


edges = []
seen = set()
dropped = []


def add(f, t, typ, as_of=TODAY, source=KNOW, conf="medium"):
    if typ == "COMPETES_WITH" and name_of[f].lower() > name_of[t].lower():
        f, t = t, f
    key = (f, t, typ)
    if key in seen:
        return
    assert f in nodes, f
    assert t in nodes, t
    seen.add(key)
    edges.append({"from_id": f, "to_id": t, "type": typ, "as_of": as_of, "source": source, "confidence": conf})


# 1. structural edges for every company
for i, r in nodes.items():
    if r["label"] != "Company":
        continue
    src = "guide" if r["source"] == "guide" else KNOW
    add(i, "ly:" + r["layer"].lower(), "OPERATES_IN", source=src, conf="high")
    add(i, "cn:" + r["country"].lower(), "HQ_IN", source=src, conf="high")

# 2. migrate v1 edges from the last v1 commit (1c16f5f), so re-running is idempotent
v1 = subprocess.run(["git", "show", "1c16f5f:data/edges.csv"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
for r in csv.DictReader(v1.splitlines()):
    if r["type"] in ("OPERATES_IN", "HQ_IN"):
        continue
    f, t = v2id(r["from_id"]), v2id(r["to_id"])
    if f is None or t is None:
        dropped.append(r)
        continue
    src = "guide" if r["source"] == "essential-guide" else r["source"]
    add(f, t, r["type"], r["as_of"], src, r["confidence"])

# 3. new edges. "S": supplies, "C": competes, "D": depends on technology, "K": controls chokepoint
S = {
 "asml": "intel sk_hynix micron", "applied_materials": "tsmc samsung intel", "lam_research": "samsung sk_hynix micron tsmc",
 "kla": "tsmc samsung intel", "tokyo_electron": "tsmc samsung intel", "asm_international": "tsmc intel",
 "advantest": "nvidia sk_hynix tsmc", "teradyne": "apple qualcomm", "screen": "tsmc samsung", "nikon": "intel",
 "besi": "tsmc intel", "onto": "tsmc", "lasertec": "tsmc samsung intel hoya agc", "disco": "tsmc sk_hynix micron",
 "kokusai": "samsung sk_hynix", "hanmi_semi": "sk_hynix micron", "kulicke_soffa": "ase amkor", "veeco": "tsmc",
 "formfactor": "intel micron sk_hynix", "camtek": "sk_hynix micron", "nova": "tsmc samsung", "aixtron": "infineon wolfspeed",
 "naura": "smic hua_hong", "amec": "smic hua_hong", "mks": "applied_materials lam_research",
 "advanced_energy": "applied_materials lam_research", "ichor": "lam_research applied_materials",
 "ultra_clean": "lam_research applied_materials",
 "shin_etsu": "tsmc samsung intel sk_hynix micron", "sumco": "tsmc samsung sk_hynix micron",
 "globalwafers": "tsmc umc globalfoundries", "siltronic": "samsung sk_hynix", "soitec": "globalfoundries stmicro",
 "tok": "tsmc samsung intel", "fujifilm": "tsmc samsung", "sumitomo_chemical": "samsung", "resonac": "tsmc ase",
 "hoya": "tsmc samsung intel", "agc": "tsmc samsung", "ajinomoto": "ibiden unimicron kinsus nanya_pcb",
 "photronics": "umc smic globalfoundries", "entegris": "tsmc samsung intel", "qnity": "tsmc samsung intel",
 "merck_kgaa": "tsmc samsung", "wacker": "shin_etsu sumco siltronic globalwafers", "linde": "tsmc samsung intel",
 "air_products": "samsung sk_hynix tsmc", "air_liquide": "tsmc samsung", "coherent": "infineon",
 "tsmc": "marvell astera_labs alchip guc novatek intel nxp analog_devices ambarella socionext",
 "umc": "mediatek realtek novatek qualcomm infineon", "globalfoundries": "qualcomm amd nxp",
 "smic": "gigadevice cambricon", "tower": "broadcom skyworks qorvo", "vanguard_intl": "novatek himax nxp",
 "psmc": "novatek", "hua_hong": "gigadevice",
 "samsung": "tesla amd apple ambarella", "sk_hynix": "amd apple", "micron": "apple amd pure_storage",
 "kioxia": "pure_storage phison", "arm": "amazon microsoft", "rambus": "samsung sk_hynix micron",
 "arteris": "nxp qualcomm", "synopsys": "nvidia intel samsung tsmc qualcomm apple",
 "cadence": "nvidia apple qualcomm samsung mediatek", "siemens": "intel tsmc", "keysight": "qualcomm",
 "empyrean": "smic hua_hong", "primarius": "smic",
 "ase": "nvidia amd qualcomm mediatek apple", "amkor": "apple qualcomm nvidia infineon", "jcet": "qualcomm",
 "powertech": "kioxia micron nanya", "kyec": "mediatek nvidia novatek", "chipbond": "novatek himax",
 "chipmos": "micron novatek", "tongfu": "amd", "ibiden": "intel nvidia amd", "unimicron": "nvidia amd intel",
 "kinsus": "amd mediatek", "nanya_pcb": "nvidia amd",
 "nvidia": "microsoft alphabet amazon meta oracle coreweave supermicro dell hpe tesla hon_hai",
 "amd": "microsoft meta oracle dell hpe supermicro", "broadcom": "alphabet meta arista cisco apple",
 "marvell": "amazon microsoft", "qualcomm": "samsung apple", "mediatek": "alphabet samsung",
 "astera_labs": "amazon microsoft", "cirrus_logic": "apple", "credo": "amazon microsoft", "monolithic_power": "nvidia",
 "sitime": "apple", "aspeed": "supermicro dell hpe quanta wiwynn", "alchip": "amazon", "silicon_motion": "kioxia micron",
 "intel": "dell hpe supermicro microsoft", "sony": "apple", "skyworks": "apple samsung", "qorvo": "apple samsung",
 "texas_instruments": "apple", "stmicro": "tesla apple", "nxp": "apple", "onsemi": "tesla",
 "montage": "samsung sk_hynix micron", "hon_hai": "apple nvidia dell hpe", "quanta": "microsoft meta amazon",
 "wiwynn": "meta microsoft", "arista": "microsoft meta", "pure_storage": "meta",
}
C = [
 "synopsys siemens", "cadence siemens", "empyrean primarius", "arm andes", "asml canon", "nikon canon",
 "applied_materials tokyo_electron", "lam_research tokyo_electron", "kla nova", "onto camtek", "advantest cohu",
 "teradyne cohu", "besi hanmi_semi", "besi kulicke_soffa", "applied_materials axcelis", "kokusai tokyo_electron",
 "kokusai asm_international", "screen tokyo_electron", "mks advanced_energy", "ichor ultra_clean", "naura amec",
 "aixtron veeco", "shin_etsu sumco", "siltronic sumco", "siltronic globalwafers", "siltronic shin_etsu",
 "tok fujifilm", "tok shin_etsu", "tok sumitomo_chemical", "hoya agc", "linde air_products", "linde air_liquide",
 "air_products air_liquide", "entegris qnity", "merck_kgaa entegris", "resonac qnity", "wolfspeed coherent",
 "tsmc intel", "samsung intel", "umc vanguard_intl", "umc psmc", "umc smic", "umc hua_hong", "smic hua_hong",
 "tower xfab", "tower db_hitek", "vanguard_intl psmc", "infineon onsemi", "infineon wolfspeed", "infineon rohm",
 "stmicro onsemi", "onsemi wolfspeed", "rohm wolfspeed", "skyworks qorvo", "diodes vishay", "wingtech diodes",
 "microchip renesas", "microchip stmicro", "nxp renesas", "nxp stmicro", "sony will_semi", "sony samsung",
 "kioxia micron", "kioxia samsung", "kioxia sk_hynix", "nanya winbond", "winbond macronix", "silicon_motion phison",
 "rambus montage", "ase jcet", "amkor jcet", "jcet hua_tian", "tongfu hua_tian", "powertech chipmos",
 "chipbond chipmos", "ibiden unimicron", "unimicron kinsus", "unimicron nanya_pcb", "ibiden nanya_pcb",
 "kinsus nanya_pcb", "nvidia broadcom", "qualcomm mediatek", "nvidia cambricon", "amd hygon", "intel hygon",
 "astera_labs credo", "astera_labs marvell", "credo marvell", "silicon_labs nordic", "silicon_labs espressif",
 "nordic espressif", "monolithic_power texas_instruments", "monolithic_power infineon", "alchip guc",
 "alchip broadcom", "alchip marvell", "socionext alchip", "macom semtech", "silergy monolithic_power",
 "rockchip mediatek", "microsoft amazon", "microsoft alphabet", "amazon alphabet", "oracle amazon",
 "oracle microsoft", "supermicro dell", "supermicro hpe", "dell hpe", "quanta wiwynn", "hon_hai quanta",
 "cisco arista", "pure_storage dell",
]
D = {
 "euv": "sk_hynix micron lasertec hoya agc tok", "hbm": "amd broadcom hanmi_semi",
 "hybrid_bonding": "besi", "cowos": "nvidia amd broadcom", "gaa": "tsmc samsung intel",
 "duv": "nikon canon umc smic globalfoundries", "dram": "sk_hynix samsung micron winbond",
 "nand": "kioxia sandisk micron sk_hynix samsung silicon_motion phison pure_storage",
 "nor_flash": "macronix winbond gigadevice",
 "silicon_carbide": "wolfspeed infineon onsemi stmicro rohm coherent aixtron tesla",
}
K = {
 "euv_mask_inspection": "lasertec", "euv_mask_blanks": "hoya agc", "abf_substrate_film": "ajinomoto",
 "hbm_memory": "micron samsung", "advanced_foundry": "samsung",
}
for f, tos in S.items():
    for t in tos.split():
        add(co[f], co[t], "SUPPLIES")
for pair in C:
    a, b = pair.split()
    add(co[a], co[b], "COMPETES_WITH")
for tech, froms in D.items():
    for f in froms.split():
        add(co[f], "te:" + tech, "DEPENDS_ON")
for cp, froms in K.items():
    for f in froms.split():
        add(co[f], "cp:" + cp, "CONTROLS")

# every chokepoint=true company must control something, and vice versa
controllers = {e["from_id"] for e in edges if e["type"] == "CONTROLS"}
for i, r in nodes.items():
    if r["label"] == "Company":
        assert (r["chokepoint"] == "true") == (i in controllers), (i, r["chokepoint"], i in controllers)

with open(ROOT / "data/edges.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["from_id", "to_id", "type", "as_of", "source", "confidence"], lineterminator="\n")
    w.writeheader(); w.writerows(edges)
from collections import Counter
print("edges:", len(edges), dict(Counter(e["type"] for e in edges)))
print("sources:", dict(Counter(e["source"] for e in edges)))
print("dropped v1 edges (unlisted endpoints):")
for r in dropped:
    print("  ", r["from_id"], r["type"], r["to_id"])

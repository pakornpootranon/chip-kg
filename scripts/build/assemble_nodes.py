"""Build data/nodes.csv from data/universe.csv + rich batches + fixed node lists."""
import csv, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))
import batch_a, batch_b, batch_c, batch_d  # noqa: E402

RICH = {}
for m in (batch_a, batch_b, batch_c, batch_d):
    for k, v in m.ROWS.items():
        assert k not in RICH, f"dup rich {k}"
        RICH[k] = v

COLS = ["id", "label", "name", "ticker", "exchange", "country", "layer", "sub_segment", "tier",
        "chokepoint", "description", "key_products", "key_customers", "fab_or_ops_geography",
        "source", "order", "code"]

LAYERS = ["EDA", "IP", "Equipment", "Materials", "Foundry", "IDM", "Memory", "Packaging", "Fabless", "EndDemand"]
TECH = ["EUV", "DUV", "HBM", "DRAM", "NAND", "NOR Flash", "CoWoS", "GAA", "Hybrid Bonding", "Silicon Carbide"]
COUNTRIES = {"US": "United States", "TW": "Taiwan", "JP": "Japan", "CN": "China", "DE": "Germany",
             "NL": "Netherlands", "KR": "South Korea", "IL": "Israel", "FR": "France", "GB": "United Kingdom",
             "SG": "Singapore", "IE": "Ireland", "BE": "Belgium", "CH": "Switzerland", "NO": "Norway"}
CHOKEPOINTS = [("euv_lithography", "EUV Lithography", "Equipment"),
               ("advanced_foundry", "Advanced Foundry (<7nm)", "Foundry"),
               ("eda_software", "EDA Software", "EDA"),
               ("hbm_memory", "HBM Memory", "Memory"),
               ("silicon_wafers", "Silicon Wafers", "Materials"),
               ("photoresist", "Photoresist", "Materials"),
               ("advanced_packaging", "Advanced Packaging", "Packaging"),
               ("euv_mask_inspection", "EUV Mask Inspection", "Equipment"),
               ("euv_mask_blanks", "EUV Mask Blanks", "Materials"),
               ("abf_substrate_film", "ABF Substrate Film", "Materials")]


def slug(s):
    return s.lower().replace(" ", "_").replace("-", "_")


rows = []
universe = list(csv.DictReader(open(ROOT / "data/universe.csv", encoding="utf-8")))
missing = [u["id"] for u in universe if u["id"].split(":", 1)[1] not in RICH]
extra = [k for k in RICH if f"co:{k}" not in {u["id"] for u in universe}]
assert not missing, f"no rich data for {missing}"
assert not extra, f"rich data for unknown {extra}"
assert universe[0]["country"] in COUNTRIES
for u in universe:
    assert u["country"] in COUNTRIES, u
    sub, desc, prod, cust, geo = RICH[u["id"].split(":", 1)[1]]
    assert "—" not in desc and "—" not in sub, u["name"]
    rows.append({"id": u["id"], "label": "Company", "name": u["name"], "ticker": u["ticker"],
                 "exchange": u["exchange"], "country": u["country"], "layer": u["layer"],
                 "sub_segment": sub, "tier": u["tier"], "chokepoint": u["chokepoint"],
                 "description": desc, "key_products": prod, "key_customers": cust,
                 "fab_or_ops_geography": geo, "source": u["source"]})
for i, name in enumerate(LAYERS, 1):
    rows.append({"id": f"ly:{slug(name)}", "label": "Layer", "name": name, "order": i})
for name in TECH:
    rows.append({"id": f"te:{slug(name)}", "label": "Technology", "name": name})
for code, name in COUNTRIES.items():
    rows.append({"id": f"cn:{code.lower()}", "label": "Country", "name": name, "code": code})
for s, name, layer in CHOKEPOINTS:
    rows.append({"id": f"cp:{s}", "label": "Chokepoint", "name": name, "layer": layer})

with open(ROOT / "data/nodes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in COLS})
from collections import Counter
print("nodes:", len(rows), dict(Counter(r["label"] for r in rows)))

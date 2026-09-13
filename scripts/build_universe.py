"""Task 2 helper: write data/universe.csv and print the counts.

Rows are hand-curated below. `source` is "guide" when the company is named
in source/guide.md, otherwise the Yahoo Finance quote page for its ticker,
which is where a follower can verify the listing.

Run: python scripts/build_universe.py
"""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = (ROOT / "source" / "guide.md").read_text(encoding="utf-8").lower()

# (slug, name, ticker, exchange, country, layer, tier, chokepoint, guide_key)
# guide_key: a lowercase substring searched in guide.md to decide source=guide.
ROWS = [
    # ---- EDA ----
    ("synopsys", "Synopsys", "SNPS", "NASDAQ", "US", "EDA", 1, True, "synopsys"),
    ("cadence", "Cadence Design Systems", "CDNS", "NASDAQ", "US", "EDA", 1, True, "cadence"),
    ("siemens", "Siemens", "SIE.DE", "XETRA", "DE", "EDA", 2, False, "siemens"),
    ("keysight", "Keysight Technologies", "KEYS", "NYSE", "US", "EDA", 3, False, "keysight"),
    ("empyrean", "Empyrean Technology", "301269.SZ", "SZSE", "CN", "EDA", 3, False, "empyrean"),
    ("silvaco", "Silvaco Group", "SVCO", "NASDAQ", "US", "EDA", 3, False, "silvaco"),
    ("primarius", "Primarius Technologies", "688206.SS", "SSE", "CN", "EDA", 3, False, "primarius"),
    # ---- IP ----
    ("arm", "Arm Holdings", "ARM", "NASDAQ", "GB", "IP", 1, False, "arm holdings"),
    ("rambus", "Rambus", "RMBS", "NASDAQ", "US", "IP", 2, False, "rambus"),
    ("ceva", "CEVA", "CEVA", "NASDAQ", "US", "IP", 2, False, "ceva"),
    ("andes", "Andes Technology", "6533.TW", "TWSE", "TW", "IP", 3, False, "andes"),
    ("verisilicon", "VeriSilicon", "688521.SS", "SSE", "CN", "IP", 3, False, "verisilicon"),
    ("arteris", "Arteris", "AIP", "NASDAQ", "US", "IP", 3, False, "arteris"),
    # ---- Equipment ----
    ("asml", "ASML", "ASML", "NASDAQ", "NL", "Equipment", 1, True, "asml"),
    ("applied_materials", "Applied Materials", "AMAT", "NASDAQ", "US", "Equipment", 2, False, "applied materials"),
    ("lam_research", "Lam Research", "LRCX", "NASDAQ", "US", "Equipment", 2, False, "lam research"),
    ("kla", "KLA", "KLAC", "NASDAQ", "US", "Equipment", 2, False, "kla"),
    ("tokyo_electron", "Tokyo Electron", "8035.T", "TSE", "JP", "Equipment", 2, False, "tokyo electron"),
    ("asm_international", "ASM International", "ASM.AS", "Euronext Amsterdam", "NL", "Equipment", 2, False, "asm international"),
    ("advantest", "Advantest", "6857.T", "TSE", "JP", "Equipment", 2, False, "advantest"),
    ("teradyne", "Teradyne", "TER", "NASDAQ", "US", "Equipment", 2, False, "teradyne"),
    ("screen", "SCREEN Holdings", "7735.T", "TSE", "JP", "Equipment", 2, False, "screen holdings"),
    ("nikon", "Nikon", "7731.T", "TSE", "JP", "Equipment", 2, False, "nikon"),
    ("canon", "Canon", "7751.T", "TSE", "JP", "Equipment", 3, False, "canon"),
    ("besi", "BE Semiconductor Industries", "BESI.AS", "Euronext Amsterdam", "NL", "Equipment", 2, False, "besi"),
    ("onto", "Onto Innovation", "ONTO", "NYSE", "US", "Equipment", 3, False, "onto innovation"),
    ("lasertec", "Lasertec", "6920.T", "TSE", "JP", "Equipment", 1, True, "lasertec"),
    ("disco", "DISCO", "6146.T", "TSE", "JP", "Equipment", 1, False, "disco corp"),
    ("kokusai", "Kokusai Electric", "6525.T", "TSE", "JP", "Equipment", 3, False, "kokusai"),
    ("hanmi_semi", "Hanmi Semiconductor", "042700.KS", "KRX", "KR", "Equipment", 2, False, "hanmi"),
    ("kulicke_soffa", "Kulicke & Soffa", "KLIC", "NASDAQ", "SG", "Equipment", 3, False, "kulicke"),
    ("axcelis", "Axcelis Technologies", "ACLS", "NASDAQ", "US", "Equipment", 3, False, "axcelis"),
    ("veeco", "Veeco Instruments", "VECO", "NASDAQ", "US", "Equipment", 3, False, "veeco"),
    ("formfactor", "FormFactor", "FORM", "NASDAQ", "US", "Equipment", 3, False, "formfactor"),
    ("camtek", "Camtek", "CAMT", "NASDAQ", "IL", "Equipment", 3, False, "camtek"),
    ("nova", "Nova", "NVMI", "NASDAQ", "IL", "Equipment", 3, False, "nova ltd"),
    ("aixtron", "Aixtron", "AIXA.DE", "XETRA", "DE", "Equipment", 3, False, "aixtron"),
    ("suss_microtec", "SUSS MicroTec", "SMHN.DE", "XETRA", "DE", "Equipment", 3, False, "suss"),
    ("naura", "NAURA Technology", "002371.SZ", "SZSE", "CN", "Equipment", 3, False, "naura"),
    ("amec", "Advanced Micro-Fabrication Equipment", "688012.SS", "SSE", "CN", "Equipment", 3, False, "amec"),
    ("mks", "MKS Instruments", "MKSI", "NASDAQ", "US", "Equipment", 3, False, "mks instruments"),
    ("advanced_energy", "Advanced Energy Industries", "AEIS", "NASDAQ", "US", "Equipment", 3, False, "advanced energy"),
    ("ichor", "Ichor Holdings", "ICHR", "NASDAQ", "US", "Equipment", 3, False, "ichor"),
    ("ultra_clean", "Ultra Clean Holdings", "UCTT", "NASDAQ", "US", "Equipment", 3, False, "ultra clean"),
    ("cohu", "Cohu", "COHU", "NASDAQ", "US", "Equipment", 3, False, "cohu"),
    # ---- Materials ----
    ("shin_etsu", "Shin-Etsu Chemical", "4063.T", "TSE", "JP", "Materials", 2, True, "shin-etsu"),
    ("sumco", "SUMCO", "3436.T", "TSE", "JP", "Materials", 2, True, "sumco"),
    ("globalwafers", "GlobalWafers", "6488.TWO", "TPEx", "TW", "Materials", 2, True, "globalwafers"),
    ("siltronic", "Siltronic", "WAF.DE", "XETRA", "DE", "Materials", 2, False, "siltronic"),
    ("soitec", "Soitec", "SOI.PA", "Euronext Paris", "FR", "Materials", 2, False, "soitec"),
    ("tok", "Tokyo Ohka Kogyo", "4186.T", "TSE", "JP", "Materials", 2, True, "tokyo ohka"),
    ("fujifilm", "Fujifilm Holdings", "4901.T", "TSE", "JP", "Materials", 3, False, "fujifilm"),
    ("sumitomo_chemical", "Sumitomo Chemical", "4005.T", "TSE", "JP", "Materials", 3, False, "sumitomo chemical"),
    ("resonac", "Resonac Holdings", "4004.T", "TSE", "JP", "Materials", 3, False, "resonac"),
    ("hoya", "HOYA", "7741.T", "TSE", "JP", "Materials", 1, True, "hoya"),
    ("agc", "AGC", "5201.T", "TSE", "JP", "Materials", 2, True, "agc inc"),
    ("ajinomoto", "Ajinomoto", "2802.T", "TSE", "JP", "Materials", 1, True, "ajinomoto"),
    ("photronics", "Photronics", "PLAB", "NASDAQ", "US", "Materials", 3, False, "photronics"),
    ("entegris", "Entegris", "ENTG", "NASDAQ", "US", "Materials", 2, False, "entegris"),
    ("qnity", "Qnity Electronics", "Q", "NYSE", "US", "Materials", 3, False, "qnity"),
    ("merck_kgaa", "Merck KGaA", "MRK.DE", "XETRA", "DE", "Materials", 3, False, "merck kgaa"),
    ("wacker", "Wacker Chemie", "WCH.DE", "XETRA", "DE", "Materials", 3, False, "wacker"),
    ("linde", "Linde", "LIN", "NASDAQ", "IE", "Materials", 3, False, "linde"),
    ("air_products", "Air Products and Chemicals", "APD", "NYSE", "US", "Materials", 3, False, "air products"),
    ("air_liquide", "Air Liquide", "AI.PA", "Euronext Paris", "FR", "Materials", 3, False, "air liquide"),
    ("coherent", "Coherent", "COHR", "NYSE", "US", "Materials", 3, False, "coherent corp"),
    # ---- Foundry ----
    ("tsmc", "TSMC", "2330.TW", "TWSE", "TW", "Foundry", 1, True, "tsmc"),
    ("umc", "United Microelectronics", "2303.TW", "TWSE", "TW", "Foundry", 2, False, "united microelectronics"),
    ("globalfoundries", "GlobalFoundries", "GFS", "NASDAQ", "US", "Foundry", 3, False, "globalfoundries"),
    ("smic", "SMIC", "0981.HK", "HKEX", "CN", "Foundry", 3, False, "smic"),
    ("tower", "Tower Semiconductor", "TSEM", "NASDAQ", "IL", "Foundry", 3, False, "tower semiconductor"),
    ("vanguard_intl", "Vanguard International Semiconductor", "5347.TWO", "TPEx", "TW", "Foundry", 3, False, "vanguard international"),
    ("psmc", "Powerchip Semiconductor Manufacturing", "6770.TW", "TWSE", "TW", "Foundry", 3, False, "powerchip"),
    ("hua_hong", "Hua Hong Semiconductor", "1347.HK", "HKEX", "CN", "Foundry", 3, False, "hua hong"),
    ("db_hitek", "DB HiTek", "000990.KS", "KRX", "KR", "Foundry", 3, False, "db hitek"),
    ("xfab", "X-FAB Silicon Foundries", "XFAB.PA", "Euronext Paris", "BE", "Foundry", 3, False, "x-fab"),
    # ---- IDM ----
    ("samsung", "Samsung Electronics", "005930.KS", "KRX", "KR", "IDM", 2, True, "samsung"),
    ("intel", "Intel", "INTC", "NASDAQ", "US", "IDM", 2, False, "intel"),
    ("texas_instruments", "Texas Instruments", "TXN", "NASDAQ", "US", "IDM", 2, False, "texas instruments"),
    ("stmicro", "STMicroelectronics", "STMPA.PA", "Euronext Paris", "CH", "IDM", 2, False, "stmicro"),
    ("nxp", "NXP Semiconductors", "NXPI", "NASDAQ", "NL", "IDM", 2, False, "nxp"),
    ("infineon", "Infineon Technologies", "IFX.DE", "XETRA", "DE", "IDM", 3, False, "infineon"),
    ("renesas", "Renesas Electronics", "6723.T", "TSE", "JP", "IDM", 2, False, "renesas"),
    ("analog_devices", "Analog Devices", "ADI", "NASDAQ", "US", "IDM", 2, False, "analog devices"),
    ("microchip", "Microchip Technology", "MCHP", "NASDAQ", "US", "IDM", 3, False, "microchip"),
    ("onsemi", "onsemi", "ON", "NASDAQ", "US", "IDM", 3, False, "onsemi"),
    ("sony", "Sony Group", "6758.T", "TSE", "JP", "IDM", 3, False, "sony"),
    ("rohm", "ROHM", "6963.T", "TSE", "JP", "IDM", 3, False, "rohm"),
    ("wolfspeed", "Wolfspeed", "WOLF", "NYSE", "US", "IDM", 3, False, "wolfspeed"),
    ("skyworks", "Skyworks Solutions", "SWKS", "NASDAQ", "US", "IDM", 3, False, "skyworks"),
    ("qorvo", "Qorvo", "QRVO", "NASDAQ", "US", "IDM", 3, False, "qorvo"),
    ("diodes", "Diodes Incorporated", "DIOD", "NASDAQ", "US", "IDM", 3, False, "diodes inc"),
    ("vishay", "Vishay Intertechnology", "VSH", "NYSE", "US", "IDM", 3, False, "vishay"),
    ("allegro", "Allegro MicroSystems", "ALGM", "NASDAQ", "US", "IDM", 3, False, "allegro"),
    ("wingtech", "Wingtech Technology", "600745.SS", "SSE", "CN", "IDM", 3, False, "wingtech"),
    # ---- Memory ----
    ("sk_hynix", "SK Hynix", "000660.KS", "KRX", "KR", "Memory", 1, True, "sk hynix"),
    ("micron", "Micron Technology", "MU", "NASDAQ", "US", "Memory", 2, True, "micron"),
    ("kioxia", "Kioxia Holdings", "285A.T", "TSE", "JP", "Memory", 2, False, "kioxia"),
    ("sandisk", "Sandisk", "SNDK", "NASDAQ", "US", "Memory", 2, False, "sandisk"),
    ("nanya", "Nanya Technology", "2408.TW", "TWSE", "TW", "Memory", 3, False, "nanya"),
    ("winbond", "Winbond Electronics", "2344.TW", "TWSE", "TW", "Memory", 3, False, "winbond"),
    ("macronix", "Macronix International", "2337.TW", "TWSE", "TW", "Memory", 3, False, "macronix"),
    ("gigadevice", "GigaDevice Semiconductor", "603986.SS", "SSE", "CN", "Memory", 3, False, "gigadevice"),
    # ---- Packaging ----
    ("ase", "ASE Technology Holding", "3711.TW", "TWSE", "TW", "Packaging", 1, True, "ase"),
    ("amkor", "Amkor Technology", "AMKR", "NASDAQ", "US", "Packaging", 2, False, "amkor"),
    ("jcet", "JCET Group", "600584.SS", "SSE", "CN", "Packaging", 2, False, "jcet"),
    ("powertech", "Powertech Technology", "6239.TW", "TWSE", "TW", "Packaging", 3, False, "powertech"),
    ("kyec", "King Yuan Electronics", "2449.TW", "TWSE", "TW", "Packaging", 3, False, "king yuan"),
    ("chipbond", "Chipbond Technology", "6147.TWO", "TPEx", "TW", "Packaging", 3, False, "chipbond"),
    ("chipmos", "ChipMOS Technologies", "8150.TW", "TWSE", "TW", "Packaging", 3, False, "chipmos"),
    ("tongfu", "Tongfu Microelectronics", "002156.SZ", "SZSE", "CN", "Packaging", 3, False, "tongfu"),
    ("hua_tian", "Tianshui Huatian Technology", "002185.SZ", "SZSE", "CN", "Packaging", 3, False, "huatian"),
    ("ibiden", "Ibiden", "4062.T", "TSE", "JP", "Packaging", 2, False, "ibiden"),
    ("unimicron", "Unimicron Technology", "3037.TW", "TWSE", "TW", "Packaging", 2, False, "unimicron"),
    ("kinsus", "Kinsus Interconnect Technology", "3189.TW", "TWSE", "TW", "Packaging", 3, False, "kinsus"),
    ("nanya_pcb", "Nan Ya PCB", "8046.TW", "TWSE", "TW", "Packaging", 3, False, "nan ya pcb"),
    # ---- Fabless ----
    ("nvidia", "NVIDIA", "NVDA", "NASDAQ", "US", "Fabless", 1, False, "nvidia"),
    ("amd", "AMD", "AMD", "NASDAQ", "US", "Fabless", 2, False, "amd"),
    ("broadcom", "Broadcom", "AVGO", "NASDAQ", "US", "Fabless", 2, False, "broadcom"),
    ("qualcomm", "Qualcomm", "QCOM", "NASDAQ", "US", "Fabless", 2, False, "qualcomm"),
    ("marvell", "Marvell Technology", "MRVL", "NASDAQ", "US", "Fabless", 2, False, "marvell"),
    ("mediatek", "MediaTek", "2454.TW", "TWSE", "TW", "Fabless", 3, False, "mediatek"),
    ("apple", "Apple", "AAPL", "NASDAQ", "US", "Fabless", 3, False, "apple"),
    ("realtek", "Realtek Semiconductor", "2379.TW", "TWSE", "TW", "Fabless", 3, False, "realtek"),
    ("novatek", "Novatek Microelectronics", "3034.TW", "TWSE", "TW", "Fabless", 3, False, "novatek"),
    ("himax", "Himax Technologies", "HIMX", "NASDAQ", "TW", "Fabless", 3, False, "himax"),
    ("lattice", "Lattice Semiconductor", "LSCC", "NASDAQ", "US", "Fabless", 3, False, "lattice"),
    ("astera_labs", "Astera Labs", "ALAB", "NASDAQ", "US", "Fabless", 3, False, "astera"),
    ("cirrus_logic", "Cirrus Logic", "CRUS", "NASDAQ", "US", "Fabless", 3, False, "cirrus"),
    ("credo", "Credo Technology", "CRDO", "NASDAQ", "US", "Fabless", 3, False, "credo"),
    ("monolithic_power", "Monolithic Power Systems", "MPWR", "NASDAQ", "US", "Fabless", 3, False, "monolithic power"),
    ("silicon_labs", "Silicon Labs", "SLAB", "NASDAQ", "US", "Fabless", 3, False, "silicon labs"),
    ("ambarella", "Ambarella", "AMBA", "NASDAQ", "US", "Fabless", 3, False, "ambarella"),
    ("semtech", "Semtech", "SMTC", "NASDAQ", "US", "Fabless", 3, False, "semtech"),
    ("macom", "MACOM Technology Solutions", "MTSI", "NASDAQ", "US", "Fabless", 3, False, "macom"),
    ("synaptics", "Synaptics", "SYNA", "NASDAQ", "US", "Fabless", 3, False, "synaptics"),
    ("power_integrations", "Power Integrations", "POWI", "NASDAQ", "US", "Fabless", 3, False, "power integrations"),
    ("sitime", "SiTime", "SITM", "NASDAQ", "US", "Fabless", 3, False, "sitime"),
    ("silicon_motion", "Silicon Motion Technology", "SIMO", "NASDAQ", "TW", "Fabless", 3, False, "silicon motion"),
    ("phison", "Phison Electronics", "8299.TWO", "TPEx", "TW", "Fabless", 3, False, "phison"),
    ("alchip", "Alchip Technologies", "3661.TW", "TWSE", "TW", "Fabless", 3, False, "alchip"),
    ("guc", "Global Unichip", "3443.TW", "TWSE", "TW", "Fabless", 3, False, "global unichip"),
    ("aspeed", "ASPEED Technology", "5274.TWO", "TPEx", "TW", "Fabless", 3, False, "aspeed"),
    ("parade", "Parade Technologies", "4966.TWO", "TPEx", "TW", "Fabless", 3, False, "parade tech"),
    ("socionext", "Socionext", "6526.T", "TSE", "JP", "Fabless", 3, False, "socionext"),
    ("silergy", "Silergy", "6415.TW", "TWSE", "CN", "Fabless", 3, False, "silergy"),
    ("montage", "Montage Technology", "688008.SS", "SSE", "CN", "Fabless", 3, False, "montage"),
    ("will_semi", "Will Semiconductor (OmniVision)", "603501.SS", "SSE", "CN", "Fabless", 3, False, "omnivision"),
    ("cambricon", "Cambricon Technologies", "688256.SS", "SSE", "CN", "Fabless", 3, False, "cambricon"),
    ("hygon", "Hygon Information Technology", "688041.SS", "SSE", "CN", "Fabless", 3, False, "hygon"),
    ("rockchip", "Rockchip Electronics", "603893.SS", "SSE", "CN", "Fabless", 3, False, "rockchip"),
    ("espressif", "Espressif Systems", "688018.SS", "SSE", "CN", "Fabless", 3, False, "espressif"),
    ("nordic", "Nordic Semiconductor", "NOD.OL", "Euronext Oslo", "NO", "Fabless", 3, False, "nordic semiconductor"),
    # ---- EndDemand ----
    ("microsoft", "Microsoft", "MSFT", "NASDAQ", "US", "EndDemand", 3, False, "microsoft"),
    ("alphabet", "Alphabet", "GOOGL", "NASDAQ", "US", "EndDemand", 3, False, "google"),
    ("amazon", "Amazon.com", "AMZN", "NASDAQ", "US", "EndDemand", 3, False, "amazon"),
    ("meta", "Meta Platforms", "META", "NASDAQ", "US", "EndDemand", 3, False, "meta platforms"),
    ("oracle", "Oracle", "ORCL", "NYSE", "US", "EndDemand", 3, False, "oracle"),
    ("tesla", "Tesla", "TSLA", "NASDAQ", "US", "EndDemand", 3, False, "tesla"),
    ("supermicro", "Super Micro Computer", "SMCI", "NASDAQ", "US", "EndDemand", 3, False, "super micro"),
    ("dell", "Dell Technologies", "DELL", "NYSE", "US", "EndDemand", 3, False, "dell"),
    ("hpe", "Hewlett Packard Enterprise", "HPE", "NYSE", "US", "EndDemand", 3, False, "hewlett packard"),
    ("cisco", "Cisco Systems", "CSCO", "NASDAQ", "US", "EndDemand", 3, False, "cisco"),
    ("arista", "Arista Networks", "ANET", "NYSE", "US", "EndDemand", 3, False, "arista"),
    ("coreweave", "CoreWeave", "CRWV", "NASDAQ", "US", "EndDemand", 3, False, "coreweave"),
    ("western_digital", "Western Digital", "WDC", "NASDAQ", "US", "EndDemand", 1, False, "western digital"),
    ("seagate", "Seagate Technology", "STX", "NASDAQ", "US", "EndDemand", 1, False, "seagate"),
    ("pure_storage", "Pure Storage", "PSTG", "NYSE", "US", "EndDemand", 3, False, "pure storage"),
    ("hon_hai", "Hon Hai Precision Industry", "2317.TW", "TWSE", "TW", "EndDemand", 3, False, "foxconn"),
    ("quanta", "Quanta Computer", "2382.TW", "TWSE", "TW", "EndDemand", 3, False, "quanta"),
    ("wiwynn", "Wiwynn", "6669.TW", "TWSE", "TW", "EndDemand", 3, False, "wiwynn"),
]

LAYERS = ["EDA", "IP", "Equipment", "Materials", "Foundry", "IDM", "Memory", "Packaging", "Fabless", "EndDemand"]


def in_guide(key):
    return re.search(r"\b" + re.escape(key), GUIDE) is not None


def main():
    out = ROOT / "data" / "universe.csv"
    slugs, names, tickers = set(), set(), set()
    rows = []
    for slug, name, ticker, exchange, country, layer, tier, cp, key in ROWS:
        assert slug not in slugs, f"duplicate slug {slug}"
        assert name not in names, f"duplicate name {name}"
        assert ticker not in tickers, f"duplicate ticker {ticker}"
        assert layer in LAYERS, f"bad layer {layer} for {name}"
        assert tier in (1, 2, 3)
        slugs.add(slug); names.add(name); tickers.add(ticker)
        source = "guide" if in_guide(key) else f"https://finance.yahoo.com/quote/{ticker}"
        rows.append({
            "id": f"co:{slug}", "name": name, "ticker": ticker, "exchange": exchange,
            "country": country, "layer": layer, "tier": tier,
            "chokepoint": "true" if cp else "false", "source": source,
        })
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    def count(field, order=None):
        c = {}
        for r in rows:
            c[r[field]] = c.get(r[field], 0) + 1
        keys = order or sorted(c, key=lambda k: -c[k])
        return "  ".join(f"{k}={c.get(k, 0)}" for k in keys)

    print(f"wrote {out.relative_to(ROOT)}: {len(rows)} companies")
    print("per layer:  ", count("layer", LAYERS))
    print("per country:", count("country"))
    print("per tier:   ", count("tier", [1, 2, 3]))
    print("chokepoint: ", sum(r["chokepoint"] == "true" for r in rows))
    print("source=guide:", sum(r["source"] == "guide" for r in rows))


if __name__ == "__main__":
    main()

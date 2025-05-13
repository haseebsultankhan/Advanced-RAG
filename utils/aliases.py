"""
Build a city‑alias dictionary from the office CSVs placed in data/raw/.
• Keys are lowercase abbreviations (e.g. "isb", "khi", "lhr")
• Values are the full, lowercase city names (e.g. "islamabad").
The module is imported by router.py at runtime, so any new city you add
to the CSVs is picked up automatically after you rerun preprocess.py.
"""
from pathlib import Path
import pandas as pd, re, unicodedata

RAW_DIR = Path("data/raw")
OFFICE_FILES = ["regional_offices.csv", "zonal_offices.csv"]

# traditional IATA codes for Pakistan's major cities
IATA = {
    "islamabad": "isb",
    "karachi": "khi",
    "lahore": "lhr",
    "peshawar": "pew",
    "quetta": "uet",
    "multan": "mux",
    "faisalabad": "lyp",
    "sialkot": "skt",
    "rawalpindi": "rwp",
    "gujranwala": "guw",
}

def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z\s]", "", text.lower()).strip()

def build_aliases() -> dict[str, str]:
    aliases = {}
    for fn in OFFICE_FILES:
        fp = RAW_DIR / fn
        if not fp.exists():
            continue
        df = pd.read_csv(fp, dtype=str, keep_default_na=False)
        # try common column names; adjust if yours differ
        for col in ("City", "city", "Location", "Office", "Office Name"):
            if col in df.columns:
                cities = {_normalize(c) for c in df[col].unique() if c}
                break
        else:
            continue  # no suitable column
        for city in cities:
            # 1. full name maps to itself
            aliases[city] = city
            # 2. IATA code if known
            if city in IATA:
                aliases[IATA[city]] = city
            # 3. first 3 letters (e.g. "isl" → islamabad)
            aliases[city[:3]] = city
            # 4. remove vowels then first 3 letters (e.g. "slm")
            no_vowels = re.sub("[aeiou]", "", city)
            aliases[no_vowels[:3]] = city
    return aliases

ALIASES: dict[str, str] = build_aliases()

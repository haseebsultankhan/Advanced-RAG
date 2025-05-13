# utils/loader.py
from pathlib import Path, PurePath
import pandas as pd, markdown, re, csv

def load_file(fp: Path) -> str:
    if fp.suffix == ".md":
        return fp.read_text(encoding="utf-8")
    if fp.suffix == ".csv":
        df = pd.read_csv(fp)            # keep commas inside quotes intact
        return df.to_markdown(index=False)
    raise ValueError(f"Unsupported extension: {fp}")

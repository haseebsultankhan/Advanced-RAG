from pathlib import Path, PurePath
import json, os, hashlib
from utils.loader import load_file
from utils.chunker import split_markdown

RAW_DIR  = Path("data/raw")
OUT_DIR  = Path("data/processed"); OUT_DIR.mkdir(parents=True, exist_ok=True)

records = []
for fp in RAW_DIR.iterdir():
    raw_text = load_file(fp)
    for i, chunk in enumerate(split_markdown(raw_text)):
        uid = hashlib.sha1(f"{fp.name}-{i}".encode()).hexdigest()[:16]
        rec = {
            "id":        uid,
            "file":      fp.name,
            "seq":       i,
            "text":      chunk
        }
        records.append(rec)
OUT_DIR.joinpath("chunks.jsonl").write_text(
    "\n".join(json.dumps(r, ensure_ascii=False) for r in records),
    encoding="utf-8"
)
print(f"Wrote {len(records)} chunks → {OUT_DIR/'chunks.jsonl'}")

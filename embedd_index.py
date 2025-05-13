import json, faiss, numpy as np, os, yaml
from pathlib import Path
from collections import defaultdict
from utils.ollama_client import embed

PROC_PATH = Path("data/processed/chunks.jsonl")
VEC_DIR   = Path("vectorstores"); VEC_DIR.mkdir(exist_ok=True)

# group by source file so each agent has its own index
by_file = defaultdict(list)
with open(PROC_PATH, encoding="utf-8") as f:
    for line in f:
        rec = json.loads(line); by_file[rec["file"]].append(rec)

for fname, recs in by_file.items():
    texts = [r["text"] for r in recs]
    embs  = np.array(embed(texts, model="bge-m3"), dtype="float32")
    d     = embs.shape[1]
    index = faiss.IndexHNSWFlat(d, 32)
    index.hnsw.efConstruction = 200
    index.add(embs)

    out_dir = VEC_DIR/fname; out_dir.mkdir(exist_ok=True)
    faiss.write_index(index, str(out_dir/"index.faiss"))
    with open(out_dir/"meta.json", "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=2)
    print(f"[{fname}] -> {len(recs)} vectors, dim={d}")

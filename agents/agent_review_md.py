\
from utils.ollama_client import complete, embed
import faiss, json, numpy as np, pathlib

AGENT_ROOT = pathlib.Path(__file__).resolve().parent.parent     # project root
IDX_DIR    = AGENT_ROOT / "vectorstores" / "review.md"

index = faiss.read_index(str(IDX_DIR / "index.faiss"))
meta  = json.load(open(IDX_DIR / "meta.json", encoding="utf-8"))

def answer(query: str, top_k: int = 4) -> str:
    q_emb = np.array(embed([query], model="bge-m3"), dtype="float32")
    dist, idx = index.search(q_emb, top_k)
    context = "\\n\\n---\\n\\n".join([meta[i]["text"] for i in idx[0]])

    prompt = f"""
You are the NADRA QA agent responsible for **review.md**.
Use the provided context to answer the user question *faithfully*.
If the context is insufficient, reply "I don't know".

Context:
{context}

Question: {query}
Answer:"""
    return complete(prompt, model="granite3.3", temperature=0.0)

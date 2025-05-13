# utils/ollama_client.py
import requests, json, os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

def _post(endpoint, payload):
    r = requests.post(f"{OLLAMA_HOST}{endpoint}", json=payload, timeout=60)
    r.raise_for_status(); return r.json()

def embed(texts, model="bge-m3", batch_size=32):
    """
    Return a list[ list[float] ] – one 1024‑d embedding per input string.
    Works with current Ollama embeddings endpoint (one prompt per call).
    """
    vectors = []
    for i in range(0, len(texts), batch_size):
        for prompt in texts[i:i+batch_size]:
            vec = _post("/api/embeddings",
                        {"model": model, "prompt": prompt})["embedding"]
            vectors.append(vec)
    return vectors


def complete(prompt, model="granite3.3", **kw):
    payload = {"model": model, "prompt": prompt, "stream": False}
    payload.update(kw)
    return _post("/api/generate", payload)["response"].strip()

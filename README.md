# Advanced Agentic RAG for NADRA Docs

## Initial Data Preparation:
1. Obtained PDF file from [NADRA Services Charter](https://www.nadra.gov.pk/nadra-services-charter/).
2. Performed OCR using Mistral OCR: [Mistral-OCR on Hugging Face](https://huggingface.co/spaces/merterbak/Mistral-OCR).
3. Copied the Markdown content and created a `.md` file, pasting the content there.
4. Split the `data.md` file into different sub `.md` files and placed them in the `raw` folder.
5. Converted `.md` files containing tables to `.csv` files (because table structure is not correctly parsed when doing embeddings with `.md` files).

Offline-first retrieval-augmented generation using local Ollama models (Granite 3.3 for reasoning, bge-m3 for embeddings) + per-file FAISS HNSW indices + an analyst layer for self-correction.

---

## 1. Quick Start

```bash
# Clone & enter
git clone https://github.com/your-org/nadra-advanced-rag.git
cd nadra-advanced-rag

# Create an env (conda or venv)
conda create -n nadra_rag python=3.10 -y
conda activate nadra_rag

# Install deps
pip install -r requirements.txt
```

## 2. Ollama Setup

1. **Install Ollama:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve                # starts the local REST server (default :11434)
```

2. **Pull required models:**

| Purpose               | Model     | Command                  |
|-----------------------|-----------|--------------------------|
| Embeddings            | bge-m3    | `ollama pull bge-m3`     |
| LLM / router / analyst| granite3.3| `ollama pull granite3.3` |

Both are quantized (≈ 1.2 GB + 4.9 GB) and run fully offline.

## 3. Project Tree

```
.
├── data/
│   └── raw/                ← drop your .md / .csv files here
├── vectorstores/           ← auto-generated FAISS indices
├── agents/                 ← auto-generated wrappers
├── utils/                  ← helper modules (chunker, device, aliases …)
├── preprocess.py           ← step 1: split & save chunks
├── embed_index.py          ← step 2: embed & build HNSW
├── agents/__init__.py      ← step 3: scaffold per-file agents
├── analyst.py              ← analyst layer (post-answer fixes)
├── router.py               ← Granite-based agent selector
└── main.py                 ← CLI entrypoint
```

## 4. End-to-End Pipeline

```bash
# 1. chunk raw docs
python preprocess.py

# 2. embed + build indices
python embed_index.py

# 3. auto-generate agent_*.py wrappers
python agents/__init__.py     # or: python -m agents if __main__.py exists

# 4. chat!
python main.py
```

You’ll see:

```
🔍 Advanced Agentic RAG + Analyst ready. Type your question, or 'exit'.
👤 >
```

## 5. Example Session

```
👤 > I’m in KHI, which NADRA office can I visit?
🤖 (regional_offices_csv) Regional Head Office, 29-E Miran Muhammad Shah Rd…

👤 > Expand CRC and FRC and state whether either incurs a fee.
🤖 (fee_md, corrected) CRC (Child Registration Certificate)… FRC (Family Registration Certificate)… both have a fee.
```

## 6. Adding / Updating Data

1. Drop new `.md` / `.csv` files into `data/raw/`.
2. Re-run steps 1–3 above to regenerate chunks, indices, and agents.
3. Restart `main.py`.

Aliases (e.g., “ISB → Islamabad”, “KHI → Karachi”) are rebuilt automatically from the office CSVs each time you restart the chat loop.

## 7. Troubleshooting

| Symptom                                      | Fix                                                                 |
|----------------------------------------------|---------------------------------------------------------------------|
| HTTPError: 400 /api/embeddings              | Ensure Ollama ≥ 0.2.0 and model bge-m3 pulled.                     |
| ModuleNotFoundError: agents.agent_fallback  | analyst.py now ships with a built-in fallback agent — regenerate agents. |
| Router picks multiple agents                | router.py trims to first token; extend to multi-agent voting if needed. |
| Need GPU speedups                           | Install CUDA, set `export OLLAMA_ORIGINS=cuda` and restart ollama. |

## 8. Extending

- **REST API** – wrap `main.py` with FastAPI to serve `/ask?q=…`.
- **Reranking** – bolt on ColBERT-v2 after FAISS for better semantics.
- **UI** – feed the API into Streamlit or a React dashboard.

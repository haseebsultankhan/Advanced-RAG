from utils.ollama_client import complete
from utils.aliases import ALIASES           # NEW import
import re, pathlib, pkgutil

AGENTS = {
    mod.name.replace("agent_", "")
    for mod in pkgutil.iter_modules([str(pathlib.Path("agents"))])
    if mod.name.startswith("agent_")
}

ROUTER_PROMPT = """\
You are an expert router.
Given a user question, decide which single agent should answer it from this list:
{agents}

Return ONLY the agent name. If none fit, return "fallback".
Question: {q}
Agent:"""

def route(user_question: str) -> str:
    # ---- 1. alias expansion ------------------------------------------------
    tokens = user_question.split()
    norm_q = " ".join(ALIASES.get(t.lower(), t) for t in tokens)

    # ---- 2. ask Granite ----------------------------------------------------
    raw = complete(
        ROUTER_PROMPT.format(agents=", ".join(AGENTS), q=norm_q),
        model="granite3.3",
        temperature=0.0,
        stop=["\n"]
    ).strip().lower()

    # ---- 3. clean Granite's reply -----------------------------------------
    candidate = re.split(r"[,\s]+", raw, maxsplit=1)[0]
    candidate = re.sub(r"[^a-z0-9_]+$", "", candidate)

    return candidate if candidate in AGENTS else "fallback"

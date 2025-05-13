"""
Analyst layer: post‑processes the primary agent’s answer.
• Extracts acronyms and key nouns.
• Queries *all* other agents for corroboration.
• Uses Granite 3.3 to repair only the wrong parts, or passes the draft through.

Put this file at project root (same level as main.py).
"""

import re, importlib, pkgutil, pathlib
from utils.ollama_client import complete

LLM_MODEL = "granite3.3"
AGENT_PKG = "agents"                       # package name
ACRONYM_RE = re.compile(r"\b([A-Z]{2,10})\b")
IGNORE = {"PKR", "USD", "CNIC", "NADRA"}   # skip obvious tokens


def list_all_agents() -> set[str]:
    """Discover all agent_<name>.py modules in the agents/ package."""
    pkg_path = pathlib.Path(__file__).parent / AGENT_PKG
    return {
        mod.name for mod in pkgutil.iter_modules([str(pkg_path)])
        if mod.name.startswith("agent_")
    }


def fetch_support(acronyms: set[str], exclude: str) -> str:
    """Query every agent except *exclude* for definitions/facts."""
    notes = []
    for mod_name in sorted(list_all_agents()):
        if mod_name == f"agent_{exclude}":
            continue
        module = importlib.import_module(f"{AGENT_PKG}.{mod_name}")
        for ac in acronyms:
            rsp = module.answer(f"What does '{ac}' stand for? Brief definition.")
            notes.append(f"{mod_name}: {ac} = {rsp}")
    return "\n".join(notes) or "No supporting information found."


def analyse(question: str, draft: str, primary: str) -> str:
    """Return corrected answer or the original draft if all good."""
    acronyms = {m.group(1) for m in ACRONYM_RE.finditer(draft)} - IGNORE
    if not acronyms:
        return draft  # nothing suspicious detected

    support = fetch_support(acronyms, exclude=primary)

    prompt = f"""
You are a system analyst verifying an agent's answer.

USER QUESTION:
{question}

PRIMARY ANSWER (from {primary}):
\"\"\"{draft}\"\"\"

REFERENCE NOTES from other domain agents:
\"\"\"{support}\"\"\"

TASK:
1. If the primary answer contains incorrect acronym expansions or factual errors
   contradicted by the notes, rewrite ONLY the incorrect snippets.
2. Preserve all correct parts verbatim.
3. If the answer is already consistent, reply exactly: KEEP

Provide the final, corrected answer only – no explanations.
"""
    revised = complete(prompt, model=LLM_MODEL, temperature=0.0).strip()
    return draft if revised == "KEEP" else revised

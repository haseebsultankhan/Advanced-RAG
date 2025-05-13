# agents/agent_fallback.py
def answer(query: str, *_, **__):
    return (
        "Sorry – I don’t have enough reliable data to answer that. "
        "Please consult an official NADRA source."
    )

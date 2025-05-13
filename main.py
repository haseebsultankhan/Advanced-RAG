import importlib
from router import route
from analyst import analyse

def loop():
    while True:
        q = input("\n👤 > ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        agent_name = route(q)
        mod = importlib.import_module(f"agents.agent_{agent_name}")
        draft = mod.answer(q)
        final = analyse(q, draft, agent_name)
        print(f"\n🤖 ({agent_name}) {final}")

if __name__ == "__main__":
    print("🔍 Advanced Agentic RAG + Analyst ready. Type your question, or 'exit'.")
    loop()

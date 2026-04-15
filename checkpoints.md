# Checkpoints

Each checkpoint lists the files in that state and how to restore to it.
For git-based rollback: `git checkout <commit> -- <file>` to restore a single file,
or `git reset --hard <commit>` to restore everything to that point.

---

## CP-001 — Baseline chatbot (2026-04-15)
**Git commit:** `4d20cfe`
**State:** Initial working CLI chatbot. Single-shot ReAct agent, FAISS RAG, Ollama llama3.

| File | State |
|---|---|
| `main.py` | CLI entry point with interactive loop |
| `agent_core.py` | Single-shot ReAct, print-only (no return value) |
| `orchestrator.py` | Routes to "info" agent, no return value |
| `tools.py` | `doc_search` k=1, `facts` stub |
| `store_docs.py` | One-time embedding script |

**Rollback:**
```bash
git reset --hard 4d20cfe
```

---

## CP-002 — Streamlit frontend + requirements (2026-04-15)
**Git commit:** uncommitted (working tree)
**State:** Streamlit chat UI added. agent_core and orchestrator now return values. requirements.txt and .gitignore added.

| File | Change |
|---|---|
| `app.py` | New — Streamlit chat frontend |
| `requirements.txt` | New — all pip dependencies |
| `.gitignore` | New — ignores __pycache__, .claude/ |
| `CLAUDE.md` | New — project feature map for Claude context |
| `agent_core.py` | `run()` now returns answer string |
| `orchestrator.py` | `run()` now returns agent result |
| `README.md` | Expanded with full module docs |

**Rollback to CP-001:**
```bash
git reset --hard 4d20cfe        # full rollback
# or per-file:
git checkout 4d20cfe -- agent_core.py orchestrator.py
rm app.py requirements.txt .gitignore CLAUDE.md
```

---

<!-- Add new checkpoints above this line as features are merged -->

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
**Git commit:** `2034d15`
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

## CP-003 — Persistent chat history + context indicator (2026-04-15)
**Git commit:** uncommitted (working tree)
**State:** 10-turn rolling history in AgentCore. Compact button summarises history via LLM. Streamlit sidebar shows context fill progress bar.

| File | Change |
|---|---|
| `agent_core.py` | Added `MAX_HISTORY`, `self.history`, `_build_history_block()`, `compact()` |
| `app.py` | Added sidebar with `st.progress()` fill bar and compact button |

**Rollback to CP-002:**
```bash
git checkout 2034d15 -- agent_core.py app.py
```

---

## CP-004 — Response style toggle (2026-04-15)
**Git commit:** uncommitted (working tree)
**State:** Concise/Explanatory mode. Style instruction injected into LLM prompt. Sidebar radio in Streamlit.

| File | Change |
|---|---|
| `agent_core.py` | Added `STYLE_INSTRUCTIONS`, `response_style` param, style note in `run()` |
| `app.py` | Added sidebar style radio + caption |

**Rollback to CP-003:**
```bash
git checkout 2034d15 -- agent_core.py app.py
# then re-apply CP-003 changes manually, or keep a CP-003 branch
```

---

<!-- Add new checkpoints above this line as features are merged -->

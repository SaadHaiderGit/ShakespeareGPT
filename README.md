# ShakespeareGPT

A locally-run chatbot for answering questions about Shakespeare's plays and sonnets. It uses a ReAct agent pattern with RAG (Retrieval-Augmented Generation) over public-domain Shakespeare texts, powered entirely by local models via Ollama — no API keys or internet connection required.

---

## Architecture

### `main.py` — Entry Point
Wires everything together and runs the interactive command-line chat loop. Defines the available tools, creates the LLM and agent, and hands control to the Orchestrator.

### `agent_core.py` — ReAct Agent
Implements the `AgentCore` class. Given a user question, it constructs a prompt using the agent's description and sends it to the LLM. The LLM responds in a structured ReAct format:

```
Thought: ...
Action: tool_name[parameter]
Observation: ...
Final Answer: ...
```

`AgentCore` parses the `Action` step with a regex, calls the matching tool, and returns the final answer to the user.

### `orchestrator.py` — Router
Implements the `Orchestrator` class. Receives user input and routes it to the correct agent. Currently routes all queries to the `info` agent. Designed to support multiple specialized agents in the future.

### `tools.py` — Tool Definitions
Defines the tools available to the agent:
- **`doc_search(query)`** — runs a FAISS similarity search (k=1) over the embedded Shakespeare documents and returns the most relevant passage.
- **`facts(topic)`** — a placeholder tool for general Shakespeare facts (stub implementation).

The FAISS vectorstore is loaded from disk once at import time.

### `store_docs.py` — Document Ingestion (One-Time Script)
Loads `ShakespearePlays.txt` and `ShakespeareSonnets.txt` from `docs/`, splits them into 2000-character chunks with 100-character overlap, embeds them using `nomic-embed-text` via Ollama, and saves the resulting FAISS index to `shakespeare_docs/`. Only needs to be run once, or re-run when the source documents change.

---

## Prerequisites

- [Ollama](https://ollama.com) installed and running locally
- The following models pulled in Ollama:
  ```
  ollama pull llama3
  ollama pull nomic-embed-text
  ```
- Python dependencies (install via pip):
  ```
  langchain langchain-community langchain-ollama langchain-text-splitters faiss-cpu
  ```

---

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/sidharthk98/ShakespeareGPT.git
   cd ShakespeareGPT
   ```

2. Install dependencies and pull Ollama models (see Prerequisites above).

3. The `shakespeare_docs/` FAISS index is included in the repo. If you want to regenerate it from scratch:
   ```
   python store_docs.py
   ```
   Note: embedding the full Shakespeare corpus takes several minutes.

4. Start the chatbot — choose one of two interfaces:

   **Option 1 — CLI**
   ```
   python main.py
   ```

   **Option 2 — Streamlit web UI**
   ```
   streamlit run app.py
   ```
   Opens in your browser at `http://localhost:8501`.

---

## Usage

### CLI
After running `main.py`, type any question about Shakespeare and press Enter. Type `exit` to quit.

```
Welcome to ShakespeareGPT. Ask a question, and our LLM chatbot will answer (type 'exit' to quit):
User: What happens in Romeo and Juliet?
LLM: ...
```

### Streamlit
After running `streamlit run app.py`, the app opens in your browser. Type your question in the chat input at the bottom and press Enter. The sidebar lets you switch between Concise and Explanatory response styles and shows how much of the conversation context has been used.

Response times vary depending on your hardware — expect up to a minute or two per query when running on CPU.

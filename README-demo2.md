# Demo 2: LangGraph - Building Agentic AI Workflows

A hands-on workshop that progressively builds a LangGraph-powered movie agent, demonstrating why graph-based orchestration matters over simple chains.

## Why LangGraph over LangChain?

| LangChain (Demo 1) | LangGraph (Demo 2) |
|---|---|
| Linear chain: prompt -> LLM -> output | Graph: nodes + edges with conditional routing |
| Single path execution | Multiple paths, loops, branching |
| Good for simple pipelines | Built for agents that reason and act |
| No control flow | Conditional edges, cycles, state management |

**In short**: LangChain is great for a straight pipeline (NL -> SQL -> Result). But when your agent needs to *decide* what to do, *use tools*, or *route to specialists* — you need a graph.

## Workshop Steps

| Step | Branch | What You Build | Key Concept |
|---|---|---|---|
| 0 | `demo2-step-0-setup` | Project scaffolding | Setup |
| 1 | `demo2-step-1-single-node` | Single movie expert node | StateGraph, nodes, edges |
| 2 | `demo2-step-2-vector-db` | + ChromaDB retrieval | Custom state, RAG, multi-node |
| 3 | `demo2-step-3-tools` | + Tools (SQL, search, Tavily) | Tool calling, agent loops |
| 4 | `demo2-step-4-multi-node` | + Router with specialists | Conditional routing |

## Graph Evolution

```
Step 1:  START -> [movie_expert] -> END

Step 2:  START -> [retrieve] -> [generate] -> END

Step 3:  START -> [agent] <-> [tools] -> END  (loop)

Step 4:  START -> [router] -+-> [movie_expert] -> END
                            +-> [sql_analyst]  -> END
                            +-> [researcher]   -> END
```

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd manipal-demo
git checkout demo2-step-0-setup

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
cp .env.example .env   # Add your API keys
pip install -r requirements.txt
python app.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## API Keys Required

| Key | Where to Get | Needed From |
|---|---|---|
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) | Step 0 |
| `TAVILY_API_KEY` | [Tavily](https://app.tavily.com/) | Step 3 |

## Tech Stack

- **Backend**: Python 3.13, Flask, LangGraph, LangChain, Google Gemini 2.5 Flash
- **Vector DB**: ChromaDB with Google Embeddings
- **Search**: Tavily Search API
- **Frontend**: React + Vite
- **Database**: SQLite (15 movies pre-loaded)

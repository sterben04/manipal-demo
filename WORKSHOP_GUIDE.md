# LangGraph Workshop - Step by Step Guide

Follow each step below. After the instructor explains a concept, run the git command to get the code for that step.

---

## Prerequisites

- Python 3.13+
- Node.js 18+
- Git
- A Google AI Studio API key ([get one here](https://aistudio.google.com/apikey))
- A Tavily API key ([get one here](https://app.tavily.com/)) — needed from Step 3

---

## Initial Setup

### 1. Clone the repo and create your working branch

```bash
git clone <repo-url>
cd manipal-demo
```

Create your own branch from the setup step:

```bash
git checkout demo2-step-0-setup
git checkout -b my-workshop
```

### 2. Set up the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

Create your `.env` file:

```bash
cp .env.example .env
```

Open `.env` and add your API keys:

```
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
python app.py
```

### 3. Set up the frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

### 4. Test Demo 1 (LangChain)

The app should already work in **SQL Mode** (Demo 1 by default). Try:

- "Show me the top rated movies"
- "Which movies made over 1 billion?"

Now click **LangGraph (Agent)** mode — it will say "not yet implemented". That's what we'll build!

---

## How to Pull Each Step

After the instructor explains each step, merge it into your branch:

```bash
git merge <branch-name>
```

If you have dependency changes, reinstall:

```bash
pip install -r requirements.txt
```

Then **restart the backend** (`Ctrl+C` and `python app.py` again).

---

## Step 1: Single Node — Your First Graph

### Merge the code

```bash
git merge demo2-step-1-single-node
```

Restart the backend:

```bash
# In the backend terminal, Ctrl+C to stop, then:
python app.py
```

### What changed

Only `backend/graph.py` — one file. Open it and look at the code:

```python
# The graph structure:
#   START -> movie_expert -> END

graph = StateGraph(MessagesState)
graph.add_node("movie_expert", movie_expert)
graph.add_edge(START, "movie_expert")
graph.add_edge("movie_expert", END)
```

### Key concepts

- **StateGraph**: The graph container that holds nodes and edges
- **MessagesState**: Built-in state type that manages a list of messages
- **Node**: A function that takes state and returns updated state
- **Edge**: Connects nodes (START -> node -> END)

### Try it

Switch to **LangGraph (Agent)** mode in the UI and ask:

- "Tell me about Inception"
- "What are some good sci-fi movies?"
- "Who directed The Dark Knight?"

**Notice**: The agent uses only its training knowledge. It doesn't have access to our movie database yet.

---

## Step 2: Vector Database — Adding Memory

### Merge the code

```bash
git merge demo2-step-2-vector-db
```

Install new dependency:

```bash
pip install -r requirements.txt
```

Restart the backend:

```bash
python app.py
```

### What changed

`backend/graph.py` now has **two nodes** and **ChromaDB**:

```python
# The graph structure:
#   START -> retrieve -> generate -> END

# Custom state with context field
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    context: str

graph = StateGraph(AgentState)
graph.add_node("retrieve", retrieve)      # Searches ChromaDB
graph.add_node("generate", generate)      # Uses context to answer
graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)
```

The `retrieve` node:
1. Takes the user's question
2. Searches ChromaDB for the 3 most relevant movies
3. Stores results in `state["context"]`

The `generate` node:
1. Reads `state["context"]` (the retrieved movies)
2. Passes it to Gemini as system context
3. Generates an informed answer

### Key concepts

- **Custom State**: `AgentState` extends beyond just messages — adds `context`
- **Sequential Nodes**: Data flows through retrieve -> generate
- **RAG Pattern**: Retrieve relevant info, then generate with it

### Try it

In **LangGraph (Agent)** mode:

- "What is the plot of The Matrix?" — now uses actual DB data!
- "Which movie has the highest revenue?" — can answer from embedded data
- "Compare Inception and Interstellar" — retrieves both and compares

**Notice**: Answers are now grounded in our actual movie database, not just the LLM's training data.

---

## Step 3: Tools — Giving the Agent Superpowers

### Merge the code

```bash
git merge demo2-step-3-tools
```

Install new dependencies:

```bash
pip install -r requirements.txt
```

Restart the backend:

```bash
python app.py
```

### What changed

`backend/graph.py` now has **3 tools** and an **agent loop**:

```python
# Tools defined:
@tool
def search_movies(query: str) -> str:       # Vector DB search
@tool
def query_movie_sql(sql_query: str) -> str:  # SQL database query
internet_search = TavilySearchResults()      # Web search

# LLM with tools bound:
llm = ChatGoogleGenerativeAI(...).bind_tools(tools)

# The graph structure (with loop!):
#   START -> agent -> (decide) -> tools -> agent -> ... -> END

graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)  # If tool call -> tools, else -> END
graph.add_edge("tools", "agent")                       # After tool runs, back to agent
```

### Key concepts

- **@tool decorator**: Wraps a function so the LLM can call it
- **bind_tools()**: Tells the LLM what tools are available
- **ToolNode**: Pre-built node that executes tool calls
- **tools_condition**: Checks if the LLM wants to use a tool or respond directly
- **Agent Loop**: agent -> tools -> agent -> tools -> ... -> END (cycles!)

### Try it

In **LangGraph (Agent)** mode:

- "What is the plot of Inception?" → uses `search_movies` (vector)
- "Show me the top 5 highest grossing movies" → uses `query_movie_sql` (SQL)
- "What movies are releasing this month?" → uses `tavily_search` (internet)
- "How much did The Dark Knight make vs Avengers Endgame?" → uses SQL tool

**Notice**: The agent **decides which tool to use** based on the question. This is the key difference — the graph now has a loop where the agent keeps reasoning until it has enough info.

---

## Step 4: Multi-Node — Router with Specialists

### Merge the code

```bash
git merge demo2-step-4-multi-node
```

Restart the backend:

```bash
python app.py
```

### What changed

`backend/graph.py` now has a **router** and **3 specialist nodes**:

```python
# Router uses structured output to classify queries:
class RouteDecision(BaseModel):
    next: Literal["movie_expert", "sql_analyst", "researcher"]

# The graph structure (branching!):
#
#                  +--> movie_expert --+
#   START -> router+--> sql_analyst  --+--> END
#                  +--> researcher   --+

graph.add_node("router", router)
graph.add_node("movie_expert", movie_expert)    # Vector DB
graph.add_node("sql_analyst", sql_analyst)      # SQL queries
graph.add_node("researcher", researcher)        # Tavily search

graph.add_edge(START, "router")
graph.add_conditional_edges("router", route_decision, {
    "movie_expert": "movie_expert",
    "sql_analyst": "sql_analyst",
    "researcher": "researcher",
})
graph.add_edge("movie_expert", END)
graph.add_edge("sql_analyst", END)
graph.add_edge("researcher", END)
```

### Key concepts

- **Structured Output**: `with_structured_output()` forces LLM to return a Pydantic model
- **Router Pattern**: One node classifies, then routes to specialists
- **Conditional Edges**: `add_conditional_edges()` with a mapping dict
- **Separation of Concerns**: Each specialist has its own tools and system prompt

### Try it

In **LangGraph (Agent)** mode:

- "Tell me about the plot of Parasite" → routes to **movie_expert** (vector DB)
- "Which movies have IMDb rating above 9?" → routes to **sql_analyst** (SQL)
- "What are the latest Christopher Nolan news?" → routes to **researcher** (Tavily)
- "How much budget did Inception have?" → routes to **sql_analyst**

**Notice**: The behavior changes based on graph structure. In Step 3, one agent decided everything. Now, a router delegates to specialists — each optimized for their task.

---

## Summary: What We Built

| Step | Graph Shape | Capability |
|---|---|---|
| 1 | Linear (1 node) | Basic chat using LLM knowledge |
| 2 | Linear (2 nodes) | RAG with vector database |
| 3 | Loop (2 nodes) | Tool-calling agent with 3 tools |
| 4 | Branching (4 nodes) | Router with specialized agents |

### LangChain vs LangGraph — Now You See Why

```
LangChain (Demo 1):
  User Question -> [NL-to-SQL Chain] -> SQL -> Result -> Display
  (One path. Always does the same thing.)

LangGraph (Demo 2, Step 4):
  User Question -> [Router] -> decides...
    -> [Movie Expert]  uses vector DB  -> Answer
    -> [SQL Analyst]   writes & runs SQL -> Answer
    -> [Researcher]    searches internet -> Answer
  (Multiple paths. Agent decides based on the question.)
```

**LangGraph gives you control over HOW the agent thinks**, not just what it thinks about.

---

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### ChromaDB errors after switching steps
Delete the generated ChromaDB folder and restart:
```bash
rm -rf backend/chroma_db
python app.py
```

### Backend won't start
Check your `.env` file has valid API keys:
```bash
cat backend/.env
```

### Merge conflicts
If you edited files and get conflicts:
```bash
git checkout --theirs backend/graph.py
git add backend/graph.py
git merge --continue
```

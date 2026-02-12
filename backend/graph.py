"""
LangGraph Movie Agent - Step 3: Tools

Agent with tools: vector search, SQL query, and internet search (Tavily).
Demonstrates: tool calling, ToolNode, conditional edges, agent loop.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from database import get_db_connection, execute_sql_query
from nl_to_sql import validate_sql_query


# -- Vector Store Setup --
def init_vector_store():
    """Initialize ChromaDB with movie data from SQLite"""
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv('GOOGLE_API_KEY')
    )

    persist_dir = os.path.join(os.path.dirname(__file__), 'chroma_db')
    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name="movies"
    )

    if vectorstore._collection.count() == 0:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.id, m.title, m.year, m.genre, m.director, m.runtime, m.description,
                   b.total_revenue, b.budget, r.imdb_rating, r.rotten_tomatoes
            FROM movies m
            LEFT JOIN box_office b ON m.id = b.movie_id
            LEFT JOIN ratings r ON m.id = r.movie_id
        ''')
        movies = cursor.fetchall()
        conn.close()

        documents, metadatas, ids = [], [], []
        for movie in movies:
            doc = (
                f"Title: {movie['title']} ({movie['year']})\n"
                f"Genre: {movie['genre']}\n"
                f"Director: {movie['director']}\n"
                f"Runtime: {movie['runtime']} minutes\n"
                f"Plot: {movie['description']}\n"
                f"Box Office: ${movie['total_revenue']}M total revenue, "
                f"${movie['budget']}M budget\n"
                f"Ratings: IMDb {movie['imdb_rating']}/10, "
                f"Rotten Tomatoes {movie['rotten_tomatoes']}%"
            )
            documents.append(doc)
            metadatas.append({
                "title": movie['title'],
                "year": movie['year'],
                "genre": movie['genre']
            })
            ids.append(str(movie['id']))

        vectorstore.add_texts(texts=documents, metadatas=metadatas, ids=ids)
        print(f"Loaded {len(documents)} movies into ChromaDB")

    return vectorstore


vectorstore = init_vector_store()


# -- Define Tools --

@tool
def search_movies(query: str) -> str:
    """Search the movie database for information about movie plots, descriptions,
    directors, and ratings. Use this for general movie questions."""
    docs = vectorstore.similarity_search(query, k=3)
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


@tool
def query_movie_sql(sql_query: str) -> str:
    """Execute a SQL query against the movie database. Only SELECT queries allowed.
    Tables: movies (id, title, year, genre, director, runtime, description),
    box_office (movie_id, domestic_revenue, international_revenue, total_revenue,
    budget, opening_weekend) - all in MILLIONS USD,
    ratings (movie_id, imdb_rating, rotten_tomatoes, metacritic, audience_score),
    cast (movie_id, person_name, role_type, character_name).
    Use aliases: m=movies, b=box_office, r=ratings, c=cast. Join on movie_id."""
    is_valid, error = validate_sql_query(sql_query)
    if not is_valid:
        return f"Error: {error}"
    result = execute_sql_query(sql_query)
    if result['success']:
        if result['row_count'] == 0:
            return "No results found."
        return str(result['data'][:10])
    return f"Error: {result.get('error', 'Unknown')}"


internet_search = TavilySearchResults(max_results=3)

tools = [search_movies, query_movie_sql, internet_search]


# -- Build Graph --

def create_graph():
    """Create agent graph with tool calling loop"""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv('GOOGLE_API_KEY'),
        temperature=0
    ).bind_tools(tools)

    def agent_node(state: MessagesState):
        """Agent node: decides whether to use tools or respond directly"""
        system = SystemMessage(content=(
            "You are a movie expert agent with access to these tools:\n"
            "1. search_movies - Search vector DB for movie plots, descriptions, info\n"
            "2. query_movie_sql - Run SQL queries for specific data (box office, ratings, cast)\n"
            "3. tavily_search_results_json - Search the internet for current movie news\n\n"
            "Choose the right tool based on the question:\n"
            "- Plot/description questions -> search_movies\n"
            "- Specific numbers/stats/comparisons -> query_movie_sql\n"
            "- Current events/news/upcoming movies -> tavily_search_results_json\n"
            "Keep final responses concise."
        ))
        response = llm.invoke([system] + state["messages"])
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    # Build graph with agent loop:
    #   START -> agent -> (tools_condition) -> tools -> agent -> ... -> END
    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile()


agent = create_graph()


def run_agent(user_message, history=None):
    """Run the agent with a user message and optional conversation history"""
    messages = []

    if history:
        for msg in history[-5:]:
            if msg.get('role') == 'user':
                messages.append(HumanMessage(content=msg.get('content', '')))
            elif msg.get('role') == 'assistant':
                content = msg.get('content') or msg.get('explanation', '')
                messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=user_message))

    result = agent.invoke({"messages": messages})
    return result["messages"][-1].content

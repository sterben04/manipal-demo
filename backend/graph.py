"""
LangGraph Movie Agent - Assignment: Add a Critic Node + Recommendation Tool

YOUR TASK:
  1. Add a new tool: get_similar_movies — finds movies similar by genre/director
  2. Add a new specialist node: critic — reviews/rates movies with a unique persona
  3. Update the router to include the new "critic" route
  4. Wire the new node into the graph

The final graph should look like:

                   +-> movie_expert  -+
  START -> router -+-> sql_analyst   -+-> END
                   +-> researcher    -+
                   +-> critic        -+   <-- NEW

Hints are marked with # TODO throughout the code.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, AnyMessage
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel, Field
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


# ============================================================
# TODO 1: Add a new tool — get_similar_movies
# ============================================================
# Create a @tool function that takes a movie title (str) and
# returns similar movies from the SQL database.
#
# Hint: Query the movies table to find the genre/director of
# the given movie, then find other movies with the same genre
# or director. Use execute_sql_query() to run the SQL.
#
# Example:
#   get_similar_movies("Inception")
#   -> Returns other Sci-Fi movies or other Christopher Nolan films
#
# @tool
# def get_similar_movies(movie_title: str) -> str:
#     """Find movies similar to the given movie by genre and director."""
#     # Step 1: Find the genre and director of the input movie
#     # Step 2: Query for movies with same genre OR same director
#     # Step 3: Return formatted results
#     pass
# ============================================================


# -- Router Schema --

# ============================================================
# TODO 2: Update RouteDecision to include "critic"
# ============================================================
# Add "critic" to the Literal type below so the router can
# route to your new node.

class RouteDecision(BaseModel):
    """Route to the appropriate specialist node"""
    next: Literal["movie_expert", "sql_analyst", "researcher"] = Field(
        # TODO: Change the Literal above to include "critic"
        description="Which specialist to handle this query"
    )

# ============================================================


# -- State with routing --

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    route: str


# -- Build Graph --

def create_graph():
    """Create multi-node graph with router and specialists"""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv('GOOGLE_API_KEY'),
        temperature=0
    )

    router_llm = llm.with_structured_output(RouteDecision)

    # -- Router Node --
    def router(state: AgentState):
        """Classify the query and decide which specialist to use"""
        system = SystemMessage(content=(
            "You are a routing agent. Based on the user's question, decide which "
            "specialist should handle it:\n\n"
            "- movie_expert: Questions about movie plots, descriptions, themes, "
            "recommendations, or general movie knowledge\n"
            "- sql_analyst: Questions needing specific data like box office numbers, "
            "ratings comparisons, cast lists, rankings, or statistical queries\n"
            "- researcher: Questions about current events, latest news, upcoming "
            "releases, or anything requiring real-time internet information\n"
            # TODO 3a: Add a description for "critic" here so the router knows
            # when to use it. Example:
            # "- critic: Questions asking for movie reviews, opinions, whether a "
            # "movie is worth watching, or comparisons of movie quality\n"
        ))
        decision = router_llm.invoke([system] + state["messages"])
        return {"route": decision.next}

    # -- Specialist: Movie Expert (Vector DB) --
    def movie_expert(state: AgentState):
        """Answer using vector search over movie descriptions"""
        last_msg = state["messages"][-1]
        query = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        docs = vectorstore.similarity_search(query, k=3)
        context = "\n\n---\n\n".join(doc.page_content for doc in docs)

        system = SystemMessage(content=(
            "You are a movie expert. Use the following movie information "
            "from the database to answer:\n\n"
            f"{context}\n\n"
            "Keep responses concise and informative."
        ))
        response = llm.invoke([system] + state["messages"])
        return {"messages": [response]}

    # -- Specialist: SQL Analyst (Database) --
    def sql_analyst(state: AgentState):
        """Answer using SQL queries against the movie database"""
        last_msg = state["messages"][-1]
        query = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)

        sql_system = SystemMessage(content=(
            "Generate a SQLite SELECT query for this question. "
            "Tables: movies (id, title, year, genre, director, runtime, description), "
            "box_office (movie_id, domestic_revenue, international_revenue, total_revenue, "
            "budget, opening_weekend) - all MILLIONS USD, "
            "ratings (movie_id, imdb_rating, rotten_tomatoes, metacritic, audience_score), "
            "cast (movie_id, person_name, role_type, character_name). "
            "Use aliases: m=movies, b=box_office, r=ratings, c=cast. "
            "Respond with ONLY the SQL query, nothing else."
        ))
        sql_response = llm.invoke([sql_system, HumanMessage(content=query)])
        sql_query = sql_response.content.strip().strip('`').replace('sql\n', '')

        is_valid, error = validate_sql_query(sql_query)
        if is_valid:
            result = execute_sql_query(sql_query)
            if result['success']:
                data_str = str(result['data'][:10])
                context = f"SQL: {sql_query}\nResults ({result['row_count']} rows): {data_str}"
            else:
                context = f"SQL failed: {result.get('error', 'Unknown')}"
        else:
            context = f"Invalid SQL: {error}"

        answer_system = SystemMessage(content=(
            "You are a data analyst. Answer the user's question based on "
            "these database results:\n\n"
            f"{context}\n\n"
            "Present the data clearly and concisely."
        ))
        response = llm.invoke([answer_system] + state["messages"])
        return {"messages": [response]}

    # -- Specialist: Researcher (Internet) --
    def researcher(state: AgentState):
        """Answer using Tavily internet search"""
        last_msg = state["messages"][-1]
        query = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)

        tavily = TavilySearchResults(max_results=3)
        results = tavily.invoke(query)
        context = "\n\n".join(
            r.get('content', '') if isinstance(r, dict) else str(r)
            for r in results
        )

        system = SystemMessage(content=(
            "You are a movie researcher with access to the latest information. "
            "Use these web search results to answer:\n\n"
            f"{context}\n\n"
            "Keep responses concise and cite sources when possible."
        ))
        response = llm.invoke([system] + state["messages"])
        return {"messages": [response]}

    # ============================================================
    # TODO 3b: Add the critic specialist node
    # ============================================================
    # Create a function called `critic` that:
    #   1. Gets the user's question from state["messages"][-1]
    #   2. Uses vectorstore.similarity_search() to find the movie
    #   3. Optionally uses your get_similar_movies tool
    #   4. Calls llm.invoke() with a fun critic persona system prompt
    #
    # Give your critic a personality! Examples:
    #   - A harsh critic who rates everything low
    #   - A nostalgic critic who loves old classics
    #   - A data-driven critic who cites ratings and box office
    #
    # def critic(state: AgentState):
    #     """Review movies with a unique critic persona"""
    #     last_msg = state["messages"][-1]
    #     query = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
    #
    #     # Search for the movie in vector DB
    #     docs = vectorstore.similarity_search(query, k=2)
    #     context = "\n\n".join(doc.page_content for doc in docs)
    #
    #     system = SystemMessage(content=(
    #         "You are a famous movie critic known for... [YOUR PERSONA HERE]. "
    #         "Review the movie based on this info:\n\n"
    #         f"{context}\n\n"
    #         "Give a rating out of 5 stars and a short, opinionated review."
    #     ))
    #     response = llm.invoke([system] + state["messages"])
    #     return {"messages": [response]}
    # ============================================================

    # -- Routing function --
    def route_decision(state: AgentState) -> str:
        return state.get("route", "movie_expert")

    # -- Build the graph --
    #
    #                  +--> movie_expert --+
    #   START -> router+--> sql_analyst  --+--> END
    #                  +--> researcher   --+
    #                  +--> critic       --+   <-- TODO 4: Add this
    #
    graph = StateGraph(AgentState)
    graph.add_node("router", router)
    graph.add_node("movie_expert", movie_expert)
    graph.add_node("sql_analyst", sql_analyst)
    graph.add_node("researcher", researcher)

    # ============================================================
    # TODO 4: Wire the critic node into the graph
    # ============================================================
    # Add these 3 lines:
    #   graph.add_node("critic", critic)
    #
    # Update the conditional edges map to include "critic":
    #   (add "critic": "critic" to the dict below)
    #
    # Add the edge from critic to END:
    #   graph.add_edge("critic", END)
    # ============================================================

    graph.add_edge(START, "router")
    graph.add_conditional_edges("router", route_decision, {
        "movie_expert": "movie_expert",
        "sql_analyst": "sql_analyst",
        "researcher": "researcher",
        # TODO: Add "critic": "critic" here
    })
    graph.add_edge("movie_expert", END)
    graph.add_edge("sql_analyst", END)
    graph.add_edge("researcher", END)
    # TODO: Add graph.add_edge("critic", END) here

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

    result = agent.invoke({"messages": messages, "route": ""})
    return result["messages"][-1].content

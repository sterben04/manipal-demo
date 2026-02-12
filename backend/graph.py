"""
LangGraph Movie Agent - Step 2: Vector DB

Two-node graph: retrieve (ChromaDB) -> generate (Gemini).
Demonstrates: multiple nodes, sequential edges, RAG pattern.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, AnyMessage
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from database import get_db_connection


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

    # Only populate if empty
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


# Initialize vector store at startup
vectorstore = init_vector_store()


# Custom state: messages + retrieved context
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    context: str


def create_graph():
    """Create a two-node graph: retrieve -> generate"""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv('GOOGLE_API_KEY'),
        temperature=0
    )

    def retrieve(state: AgentState):
        """Node 1: Search vector DB for relevant movies"""
        last_msg = state["messages"][-1]
        query = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        docs = vectorstore.similarity_search(query, k=3)
        context = "\n\n---\n\n".join(doc.page_content for doc in docs)
        return {"context": context}

    def generate(state: AgentState):
        """Node 2: Generate response using retrieved context"""
        context = state.get("context", "")
        system = SystemMessage(content=(
            "You are a movie expert with access to a movie database. "
            "Use the following retrieved movie information to answer:\n\n"
            f"{context}\n\n"
            "If the information doesn't fully answer the question, "
            "supplement with your general knowledge. Keep responses concise."
        ))
        response = llm.invoke([system] + state["messages"])
        return {"messages": [response]}

    # Build graph: START -> retrieve -> generate -> END
    graph = StateGraph(AgentState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

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

    result = agent.invoke({"messages": messages, "context": ""})
    return result["messages"][-1].content

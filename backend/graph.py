"""
LangGraph Movie Agent - Step 1: Single Node

A simple single-node graph that uses Gemini to answer movie questions.
This demonstrates the basic LangGraph structure: State -> Node -> Edge.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END


def create_graph():
    """Create a single-node LangGraph agent"""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv('GOOGLE_API_KEY'),
        temperature=0
    )

    def movie_expert(state: MessagesState):
        """Single node: answers movie questions using Gemini"""
        system = SystemMessage(content=(
            "You are a movie expert. You know everything about films, directors, "
            "actors, box office numbers, and the film industry. "
            "Answer questions concisely and informatively. "
            "If you don't know something, say so honestly."
        ))
        response = llm.invoke([system] + state["messages"])
        return {"messages": [response]}

    # Build the graph: START -> movie_expert -> END
    graph = StateGraph(MessagesState)
    graph.add_node("movie_expert", movie_expert)
    graph.add_edge(START, "movie_expert")
    graph.add_edge("movie_expert", END)

    return graph.compile()


# Compile once at module level
agent = create_graph()


def run_agent(user_message, history=None):
    """Run the agent with a user message and optional conversation history"""
    messages = []

    # Convert history to LangChain message format
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

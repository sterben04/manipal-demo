# Assignment: Add a Movie Critic Node + Recommendation Tool

## Overview

Extend the LangGraph movie agent by adding:
1. A **new tool** (`get_similar_movies`) that finds similar movies by genre/director
2. A **new specialist node** (`critic`) that reviews movies with a unique persona
3. Wire everything into the existing router graph

## Setup

```bash
git checkout demo2-assignment
git checkout -b my-assignment
pip install -r requirements.txt
python app.py
```

## Your Tasks

Open `backend/graph.py` — all 4 TODOs are clearly marked.

### TODO 1: Create the `get_similar_movies` tool

Write a `@tool` function that:
- Takes a movie title as input
- Queries the SQL database to find the movie's genre and director
- Returns other movies with the same genre OR director

```python
@tool
def get_similar_movies(movie_title: str) -> str:
    """Find movies similar to the given movie by genre and director."""
    # Your code here
```

**Hint**: Use two SQL queries with `execute_sql_query()`:
```sql
-- Step 1: Get the movie's genre and director
SELECT genre, director FROM movies WHERE LOWER(title) LIKE '%inception%'

-- Step 2: Find similar movies
SELECT title, year, genre, director FROM movies
WHERE (genre = 'Sci-Fi' OR director = 'Christopher Nolan')
AND title != 'Inception'
```

### TODO 2: Update the `RouteDecision` schema

Add `"critic"` to the `Literal` type:

```python
# Before:
next: Literal["movie_expert", "sql_analyst", "researcher"]

# After:
next: Literal["movie_expert", "sql_analyst", "researcher", "critic"]
```

### TODO 3: Add the `critic` node + update router prompt

**3a.** Add a description for `critic` in the router's system prompt so it knows when to route there.

**3b.** Write the `critic` function. Use `vectorstore.similarity_search()` to get movie data, then pass it to the LLM with a fun critic persona.

Give your critic a personality! Be creative:
- A harsh critic who rarely gives above 3 stars
- A nostalgic critic who thinks nothing beats 90s cinema
- A data nerd who compares box office and ratings obsessively
- A poetic critic who writes in metaphors

### TODO 4: Wire the node into the graph

Three additions:
```python
graph.add_node("critic", critic)                    # Register the node
# Add "critic": "critic" to conditional edges dict  # Connect router -> critic
graph.add_edge("critic", END)                       # Connect critic -> END
```

## Testing

After completing all TODOs, restart the backend and try these in **Agent Mode**:

| Query | Expected Route |
|---|---|
| "Review The Dark Knight for me" | critic |
| "Is Inception worth watching?" | critic |
| "What's the plot of Parasite?" | movie_expert |
| "Top 5 highest grossing movies" | sql_analyst |
| "Latest Marvel movie news" | researcher |

## Bonus Challenges

If you finish early:

1. **Use the `get_similar_movies` tool inside your critic node** — after reviewing a movie, suggest similar ones
2. **Add a second persona** — create a `critic_2` node with a different personality, and update the router to choose between them based on the question tone
3. **Add a `summarizer` node** — a final node that runs after any specialist and summarizes the response in exactly 2 sentences

## Submission

Push your branch:
```bash
git add backend/graph.py
git commit -m "assignment: add critic node and recommendation tool"
git push origin my-assignment
```

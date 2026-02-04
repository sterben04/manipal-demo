# Backend API

Flask backend API with natural language to SQL query capabilities using LangChain and Google Gemini.

## Features

- Natural language to SQL conversion using Google Gemini AI
- SQLite database with movie data (4 normalized tables)
- RESTful API endpoints
- Query validation and safety checks
- Structured JSON responses with query results
- LangSmith integration for tracing and monitoring (optional)

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the backend directory:
```bash
# Required: Google API Key for Gemini
GOOGLE_API_KEY=your_google_api_key_here

# Optional: LangSmith for tracing and monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=manipal-demo-nl-to-sql
```

**Required Keys:**
- Get your Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

**Optional - LangSmith Tracing:**
- Sign up at [LangSmith](https://smith.langchain.com/)
- Get your API key from LangSmith settings
- LangSmith provides tracing, monitoring, and debugging for LangChain operations
- If not configured, the app will work normally without tracing

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5001`

The database will be automatically initialized with dummy movie data on the first run.

## API Endpoints

### POST /query
Converts natural language queries to SQL and executes them against the database.

**Request:**
```json
{
  "message": "Show me the top rated movies"
}
```

**Success Response:**
```json
{
  "status": "success",
  "user_message": "Show me the top rated movies",
  "sql": "SELECT * FROM movies ORDER BY rating DESC LIMIT 10",
  "explanation": "Retrieves the top 10 movies sorted by rating in descending order",
  "data": [
    {
      "id": 1,
      "title": "The Shawshank Redemption",
      "year": 1994,
      "genre": "Drama",
      "rating": 9.3,
      ...
    }
  ],
  "columns": ["id", "title", "year", "genre", "director", "rating", "box_office", "runtime", "description"],
  "row_count": 10
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": "Error message describing what went wrong"
}
```

**Example Queries:**
- "Show me the top rated movies"
- "Which movies made over 1 billion dollars?"
- "List all Sci-Fi movies"
- "Who directed The Dark Knight?"
- "What are the longest movies in the database?"

### GET /health
Health check endpoint to verify the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

### GET /movies
Retrieve all movies or filter by genre.

**Query Parameters:**
- `genre` (optional): Filter movies by genre (e.g., "Action", "Drama", "Sci-Fi")

**Response:**
```json
{
  "movies": [
    {
      "id": 1,
      "title": "The Shawshank Redemption",
      "year": 1994,
      "genre": "Drama",
      "director": "Frank Darabont",
      "rating": 9.3,
      "box_office": 28.3,
      "runtime": 142,
      "description": "Two imprisoned men bond over a number of years..."
    }
  ],
  "count": 15,
  "status": "success"
}
```

**Example:**
- Get all movies: `GET http://localhost:5001/movies`
- Filter by genre: `GET http://localhost:5001/movies?genre=Action`

### GET /movies/:id
Retrieve a specific movie by ID.

**Response:**
```json
{
  "movie": {
    "id": 1,
    "title": "The Shawshank Redemption",
    "year": 1994,
    "genre": "Drama",
    "director": "Frank Darabont",
    "rating": 9.3,
    "box_office": 28.3,
    "runtime": 142,
    "description": "Two imprisoned men bond over a number of years..."
  },
  "status": "success"
}
```

## Database

The application uses SQLite to store movie data. The database file (`movies.db`) is automatically created and populated with 15 popular movies on the first run.

### Schema

The complete database schema is documented in `schema.json`. This file contains the structure of all tables, column definitions, constraints, and descriptions.

**Movies Table:**
- `id`: Integer (Primary Key, Auto-increment) - Unique identifier
- `title`: Text (NOT NULL) - Movie title
- `year`: Integer (NOT NULL) - Release year
- `genre`: Text (NOT NULL) - Primary genre
- `director`: Text (NOT NULL) - Director name
- `rating`: Real (NOT NULL) - Rating out of 10
- `box_office`: Real - Box office revenue in millions (USD)
- `runtime`: Integer - Runtime in minutes
- `description`: Text - Brief description or synopsis

For detailed schema information including constraints and field descriptions, refer to `schema.json`.

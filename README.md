# Manipal Demo - Natural Language to SQL Query Application

A full-stack application that allows users to query a movie database using natural language. The application converts natural language questions into SQL queries using Google Gemini AI via LangChain, executes them safely, and displays the results in an intuitive table format.

## Features

- 🤖 **Natural Language Queries**: Ask questions in plain English
- 🔍 **SQL Generation**: Automatic conversion to SQL using Google Gemini AI
- 🛡️ **Query Validation**: Safety checks to prevent harmful queries
- 📊 **Visual Results**: Beautiful table display of query results
- 💬 **Chat Interface**: ChatGPT-like UI for seamless interaction
- 🎬 **Movie Database**: Pre-populated with 15 popular movies

## Tech Stack

### Backend
- **Flask**: Python web framework
- **SQLite**: Lightweight database
- **LangChain**: AI framework for LLM integration
- **Google Gemini**: AI model for natural language processing
- **LangSmith**: Tracing and monitoring for LangChain (optional)

### Frontend
- **React**: UI library
- **Vite**: Build tool and dev server
- **CSS3**: Styling

## Project Structure

```
manipal-demo/
├── backend/
│   ├── app.py              # Flask application
│   ├── database.py         # Database operations
│   ├── nl_to_sql.py        # Natural language to SQL conversion
│   ├── schema.json         # Database schema definition
│   ├── requirements.txt    # Python dependencies
│   └── README.md           # Backend documentation
└── frontend/
    ├── src/
    │   ├── components/     # React components
    │   ├── App.jsx         # Main application
    │   └── App.css         # Styles
    └── README.md           # Frontend documentation
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Google API Key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))
- LangSmith API Key (optional, for tracing - get from [LangSmith](https://smith.langchain.com/))

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```bash
# Required
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env

# Optional: Add LangSmith for tracing
echo "LANGCHAIN_TRACING_V2=true" >> .env
echo "LANGCHAIN_API_KEY=your_langsmith_api_key_here" >> .env
echo "LANGCHAIN_PROJECT=manipal-demo-nl-to-sql" >> .env
```

**Note:** LangSmith is optional. The app works without it, but LangSmith provides valuable tracing and monitoring capabilities for debugging and optimizing your LangChain operations.

5. Run the Flask server:
```bash
python app.py
```

The backend will start on `http://localhost:5001`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will start on `http://localhost:5173`

## Usage

Once both servers are running:

1. Open your browser to `http://localhost:5173`
2. Type natural language queries about movies, such as:
   - "Show me the top rated movies"
   - "Which movies made over 1 billion dollars?"
   - "List all Sci-Fi movies"
   - "Who directed The Dark Knight?"
   - "What are the longest movies?"

The application will:
1. Convert your query to SQL
2. Display the generated SQL and explanation
3. Show the results in a formatted table

## Database Schema

The application uses a normalized database structure with 4 related tables:

### 1. **movies** - Core movie information
- `id`, `title`, `year`, `genre`, `director`, `runtime`, `description`

### 2. **box_office** - Financial data
- `movie_id` (FK), `domestic_revenue`, `international_revenue`, `total_revenue`, `budget`, `opening_weekend`

### 3. **ratings** - Rating information
- `movie_id` (FK), `imdb_rating`, `rotten_tomatoes`, `metacritic`, `audience_score`

### 4. **cast** - Actors and crew
- `movie_id` (FK), `person_name`, `role_type`, `character_name`

This normalized structure allows for complex queries like:
- "Show movies with box office over $500M and ratings above 8.5"
- "Which actors appeared in Christopher Nolan films?"
- "Compare domestic vs international revenue for Sci-Fi movies"

See `backend/schema.json` for the complete schema definition.

## API Endpoints

### POST /query
Convert natural language to SQL and execute query
- Request: `{ "message": "your question" }`
- Response: SQL, explanation, data, and results

### GET /health
Health check endpoint

All data queries go through the natural language `/query` endpoint - there are no direct REST endpoints for accessing specific tables.

## Safety Features

- Only SELECT queries are allowed
- Query validation prevents harmful SQL operations
- No INSERT, UPDATE, DELETE, DROP, or other modifying operations
- All queries are sanitized and validated before execution

## Monitoring with LangSmith (Optional)

LangSmith provides powerful tracing and monitoring for your LangChain operations:

### Setup:
1. Sign up at [smith.langchain.com](https://smith.langchain.com/)
2. Get your API key from settings
3. Add to your `.env` file:
   ```bash
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_api_key
   LANGCHAIN_PROJECT=manipal-demo-nl-to-sql
   ```

### Benefits:
- **Trace LLM calls**: See exactly what prompts are sent to Gemini
- **Monitor performance**: Track latency and token usage
- **Debug issues**: View failed queries and error details
- **Optimize prompts**: A/B test different prompt strategies
- **View conversations**: See the full chain execution flow

### Accessing Traces:
Once configured, visit your LangSmith dashboard to view:
- All natural language → SQL conversions
- Prompt templates and responses
- Execution times and costs
- Error rates and failure patterns

## Development

### Adding New Tables

1. Update `backend/schema.json` with the new table structure
2. Modify `backend/database.py` to create and populate the table
3. Restart the backend server

### Modifying the Frontend

The main components are:
- `App.jsx`: Main application logic and state management
- `ChatWindow.jsx`: Chat interface and message display
- `ResultsTable.jsx`: Query results table component
- `Sidebar.jsx`: Session management sidebar

## License

This project is for demonstration purposes.

## Support

For issues or questions, please refer to the individual README files in the backend and frontend directories.

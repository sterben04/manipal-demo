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

4. Create a `.env` file with your Google API key:
```bash
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
```

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

The application includes a movies table with the following columns:

- `id`: Unique identifier (Primary Key)
- `title`: Movie title
- `year`: Release year
- `genre`: Movie genre
- `director`: Director name
- `rating`: Rating out of 10
- `box_office`: Box office revenue in millions (USD)
- `runtime`: Runtime in minutes
- `description`: Brief synopsis

See `backend/schema.json` for the complete schema definition.

## API Endpoints

### POST /query
Convert natural language to SQL and execute query
- Request: `{ "message": "your question" }`
- Response: SQL, explanation, data, and results

### GET /movies
Get all movies or filter by genre
- Query params: `genre` (optional)

### GET /movies/:id
Get a specific movie by ID

### GET /health
Health check endpoint

## Safety Features

- Only SELECT queries are allowed
- Query validation prevents harmful SQL operations
- No INSERT, UPDATE, DELETE, DROP, or other modifying operations
- All queries are sanitized and validated before execution

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

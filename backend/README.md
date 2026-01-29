# Backend API

Flask backend API for the manipal-demo application.

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

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5001`

## API Endpoints

### POST /query
Receives messages from the frontend and returns a response.

**Request:**
```json
{
  "message": "user message here"
}
```

**Response:**
```json
{
  "reply": "response message",
  "status": "success"
}
```

### GET /health
Health check endpoint to verify the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

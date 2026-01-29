# Chatbot UI Demo

A minimal chatbot interface built with React, similar to ChatGPT.

## Features

- Left sidebar with chat sessions
- Main chat window with message display
- Message input for user interaction
- Simulated bot responses
- Clean, modern UI inspired by ChatGPT

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open your browser to the URL shown in the terminal (typically http://localhost:5173)

## Project Structure

- `src/App.jsx` - Main app component with state management
- `src/components/Sidebar.jsx` - Left sidebar for chat sessions
- `src/components/ChatWindow.jsx` - Main chat interface
- CSS files for styling each component

## Customization

The bot currently returns a demo response. To connect to a real AI API, modify the `handleSendMessage` function in `App.jsx` to call your backend/API endpoint.

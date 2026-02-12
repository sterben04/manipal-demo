import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import './App.css'

function App() {
  const [sessions, setSessions] = useState([
    { id: 1, title: 'New Chat 1', messages: [] }
  ])
  const [activeSessionId, setActiveSessionId] = useState(1)
  const [mode, setMode] = useState('sql') // 'sql' or 'agent'

  const activeSession = sessions.find(s => s.id === activeSessionId)

  const handleNewChat = () => {
    const newSession = {
      id: Date.now(),
      title: `New Chat ${sessions.length + 1}`,
      messages: []
    }
    setSessions([...sessions, newSession])
    setActiveSessionId(newSession.id)
  }

  const handleSendMessage = async (message) => {
    // Get the current active session to extract its history
    const currentSession = sessions.find(s => s.id === activeSessionId)
    
    // Convert message history to the format expected by backend
    const conversationHistory = currentSession?.messages.map(msg => {
      if (msg.isUser) {
        return {
          role: 'user',
          content: msg.text
        }
      } else {
        return {
          role: 'assistant',
          sql: msg.queryResult?.sql || '',
          explanation: msg.queryResult?.explanation || ''
        }
      }
    }) || []

    // Add user message immediately and update title if it's the first message
    setSessions(sessions.map(session => {
      if (session.id === activeSessionId) {
        const updatedMessages = [
          ...session.messages,
          { id: Date.now(), text: message, isUser: true }
        ]
        
        // Update title with first message (truncated to 30 chars)
        const newTitle = session.messages.length === 0 
          ? (message.length > 30 ? message.substring(0, 30) + '...' : message)
          : session.title
        
        return {
          ...session,
          title: newTitle,
          messages: updatedMessages
        }
      }
      return session
    }))

    // Call backend API with conversation history
    const endpoint = mode === 'agent' ? 'http://localhost:5001/agent' : 'http://localhost:5001/query'

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          history: conversationHistory
        })
      })

      const data = await response.json()

      if (mode === 'agent' && data.status === 'success') {
        // Agent mode: text response
        setSessions(prev => prev.map(s => {
          if (s.id === activeSessionId) {
            return {
              ...s,
              messages: [
                ...s.messages,
                { id: Date.now(), text: data.response, isUser: false }
              ]
            }
          }
          return s
        }))
      } else if (data.status === 'success' && data.data) {
        // SQL mode: query results
        setSessions(prev => prev.map(s => {
          if (s.id === activeSessionId) {
            return {
              ...s,
              messages: [
                ...s.messages,
                {
                  id: Date.now(),
                  text: null,
                  queryResult: {
                    sql: data.sql,
                    explanation: data.explanation,
                    data: data.data,
                    columns: data.columns,
                    row_count: data.row_count
                  },
                  isUser: false
                }
              ]
            }
          }
          return s
        }))
      } else {
        setSessions(prev => prev.map(s => {
          if (s.id === activeSessionId) {
            return {
              ...s,
              messages: [
                ...s.messages,
                {
                  id: Date.now(),
                  text: data.error || 'Sorry, I could not process your request.',
                  isUser: false
                }
              ]
            }
          }
          return s
        }))
      }
    } catch (error) {
      console.error('Error calling backend:', error)
      setSessions(prev => prev.map(s => {
        if (s.id === activeSessionId) {
          return {
            ...s,
            messages: [
              ...s.messages,
              {
                id: Date.now(),
                text: 'Sorry, there was an error connecting to the server. Please make sure the backend is running.',
                isUser: false
              }
            ]
          }
        }
        return s
      }))
    }
  }

  return (
    <div className="app">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={setActiveSessionId}
        onNewChat={handleNewChat}
      />
      <ChatWindow
        session={activeSession}
        onSendMessage={handleSendMessage}
        mode={mode}
        onModeChange={setMode}
      />
    </div>
  )
}

export default App

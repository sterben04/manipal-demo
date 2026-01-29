import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import './App.css'

function App() {
  const [sessions, setSessions] = useState([
    { id: 1, title: 'New Chat 1', messages: [] }
  ])
  const [activeSessionId, setActiveSessionId] = useState(1)

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
    // Add user message immediately
    setSessions(sessions.map(session => {
      if (session.id === activeSessionId) {
        return {
          ...session,
          messages: [
            ...session.messages,
            { id: Date.now(), text: message, isUser: true }
          ]
        }
      }
      return session
    }))

    // Call backend API
    try {
      const response = await fetch('http://localhost:5001/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message })
      })

      const data = await response.json()

      // Add bot response
      setSessions(prev => prev.map(s => {
        if (s.id === activeSessionId) {
          return {
            ...s,
            messages: [
              ...s.messages,
              { 
                id: Date.now(), 
                text: data.reply || 'Sorry, I could not process your request.', 
                isUser: false 
              }
            ]
          }
        }
        return s
      }))
    } catch (error) {
      console.error('Error calling backend:', error)
      // Add error message
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
      />
    </div>
  )
}

export default App

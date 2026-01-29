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

  const handleSendMessage = (message) => {
    setSessions(sessions.map(session => {
      if (session.id === activeSessionId) {
        const newMessages = [
          ...session.messages,
          { id: Date.now(), text: message, isUser: true }
        ]
        
        // Simulate bot response
        setTimeout(() => {
          setSessions(prev => prev.map(s => {
            if (s.id === activeSessionId) {
              return {
                ...s,
                messages: [
                  ...s.messages,
                  { 
                    id: Date.now(), 
                    text: 'This is a demo response. In a real app, this would be connected to an AI API.', 
                    isUser: false 
                  }
                ]
              }
            }
            return s
          }))
        }, 500)

        return { ...session, messages: newMessages }
      }
      return session
    }))
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

import { useState, useRef, useEffect } from 'react'
import ResultsTable from './ResultsTable'
import './ChatWindow.css'

function ChatWindow({ session, onSendMessage }) {
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [session?.messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (inputValue.trim()) {
      onSendMessage(inputValue)
      setInputValue('')
    }
  }

  return (
    <div className="chat-window">
      <div className="messages-container">
        {session?.messages.length === 0 ? (
          <div className="empty-state">
            <h2>Start a conversation</h2>
            <p>Ask questions about the movie database</p>
            <div className="example-queries">
              <p><strong>Try asking:</strong></p>
              <ul>
                <li>"Show me the top rated movies"</li>
                <li>"Which movies made over 1 billion?"</li>
                <li>"List all Sci-Fi movies"</li>
                <li>"Who directed The Dark Knight?"</li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="messages">
            {session?.messages.map(message => (
              <div
                key={message.id}
                className={`message ${message.isUser ? 'user-message' : 'bot-message'}`}
              >
                <div className="message-avatar">
                  {message.isUser ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  {message.text && <div className="message-text">{message.text}</div>}
                  {message.queryResult && (
                    <ResultsTable
                      data={message.queryResult.data}
                      columns={message.queryResult.columns}
                      sql={message.queryResult.sql}
                      explanation={message.queryResult.explanation}
                      rowCount={message.queryResult.row_count}
                    />
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="input-container">
        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            className="message-input"
            placeholder="Ask about movies..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
          />
          <button
            type="submit"
            className="send-btn"
            disabled={!inputValue.trim()}
          >
            ➤
          </button>
        </form>
      </div>
    </div>
  )
}

export default ChatWindow

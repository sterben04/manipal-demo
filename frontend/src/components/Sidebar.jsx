import './Sidebar.css'

function Sidebar({ sessions, activeSessionId, onSelectSession, onNewChat }) {
  return (
    <div className="sidebar">
      <button className="new-chat-btn" onClick={onNewChat}>
        + New Chat
      </button>
      
      <div className="sessions-list">
        {sessions.map(session => (
          <div
            key={session.id}
            className={`session-item ${session.id === activeSessionId ? 'active' : ''}`}
            onClick={() => onSelectSession(session.id)}
          >
            <span className="session-icon">💬</span>
            <span className="session-title">{session.title}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Sidebar

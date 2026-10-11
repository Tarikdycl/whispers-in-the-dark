function StoryPanel({ messages }) {
  return (
    <div className="panel story-panel">
      <div className="panel-header">
        <h2>Story</h2>
      </div>

      <div className="story-log">
        {messages.map((message, index) => (
          <div
            key={index}
            className={
              message.type === "player"
                ? "message player-message"
                : "message system-message"
            }
          >
            {message.type === "player" ? (
              <>
                <span className="message-label">You</span>
                <p>{message.text}</p>
              </>
            ) : (
              <>
                <span className="message-label">Narrator</span>
                <p>{message.text}</p>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default StoryPanel;

import { useState } from "react";

function ActionInput({ onSubmit }) {
  const [input, setInput] = useState("");

  const suggestions = [
    "I look around",
    "I wait",
    "I take the rock",
    "I run",
    "I listen carefully",
  ];

  function handleSubmit(event) {
    event.preventDefault();

    if (!input.trim()) return;

    onSubmit(input);
    setInput("");
  }

  function handleSuggestion(action) {
    onSubmit(action);
    setInput("");
  }

  return (
    <div className="panel action-panel">
      <div className="panel-header">
        <h2>What do you do?</h2>
      </div>

      <form className="action-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="action-input"
          placeholder="Describe your next action..."
          value={input}
          onChange={(event) => setInput(event.target.value)}
        />

        <button type="submit" className="action-button">
          Send
        </button>
      </form>

      <div className="suggestions">
        {suggestions.map((action) => (
          <button
            key={action}
            type="button"
            className="suggestion-chip"
            onClick={() => handleSuggestion(action)}
          >
            {action}
          </button>
        ))}
      </div>
    </div>
  );
}

export default ActionInput;

import { useState } from "react";

function ActionInput({ onSubmit }) {
  const [input, setInput] = useState("");

  const suggestions = [
    "I look around",
    "I wait",
    "I take the rock",
    "I walk forward",
    "I listen carefully",
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(input);
    setInput("");
  };

  return (
    <div className="panel action-panel">
      <div className="panel-header">
        <h2>What do you do?</h2>
      </div>

      <form onSubmit={handleSubmit} className="action-form">
        <input
          type="text"
          placeholder="Type your action..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="action-input"
        />
        <button type="submit" className="action-button">
          Send
        </button>
      </form>

      <div className="suggestions">
        {suggestions.map((item) => (
          <button
            key={item}
            className="suggestion-chip"
            onClick={() => onSubmit(item)}
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}

export default ActionInput;
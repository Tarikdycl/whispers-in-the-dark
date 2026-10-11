
import { useState } from "react";
import "./styles/app.css";

// Our available game worlds
const worlds = [
  {
    id: "hospital",
    name: "The Hospital",
    year: "1980",
    theme: "Zombie Apocalypse",
    opening:
      "You wake up in an abandoned hospital. The lights flicker above you. Somewhere down the corridor, you hear footsteps dragging across the floor.",
  },
  {
    id: "forest",
    name: "The Forest",
    year: "1870",
    theme: "Europe",
    opening:
      "You wake on cold, wet soil. Ancient trees surround you. Moonlight passes through the branches. Something is watching from the darkness.",
  },
  {
    id: "city",
    name: "The Last City",
    year: "2080",
    theme: "AI Apocalypse",
    opening:
      "The city has been silent for days. Drones patrol the empty streets. A mechanical voice whispers through a broken radio: We know you're here.",
  },
];

function App() {
  // Controls which screen is displayed
  const [screen, setScreen] = useState("landing");
  const [transitioning, setTransitioning] = useState(false);

  // Current game world
  const [world, setWorld] = useState(null);

  // Game information
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [health, setHealth] = useState(100);
  const [hunger, setHunger] = useState(0);

  // Fade out, change screen, then fade in
  function changeScreen(nextScreen, callback) {
    if (transitioning) return;

    setTransitioning(true);

    setTimeout(() => {
      if (callback) callback();
      setScreen(nextScreen);
      setTransitioning(false);
    }, 700);
  }

  // Enter the selected world
  function startWorld(selectedWorld) {
    changeScreen("game", () => {
      setWorld(selectedWorld);
      setMessages([
        {
          role: "narrator",
          text: selectedWorld.opening,
        },
      ]);
      setHealth(100);
      setHunger(0);
      setInput("");
    });
  }

  // Temporary gameplay until the LLM is connected
  function handleAction(event) {
    event.preventDefault();

    const action = input.trim();
    if (!action) return;

    const response =
      "You hear something moving in the distance. The darkness seems to grow heavier around you.";

    setMessages((previous) => [
      ...previous,
      { role: "player", text: action },
      { role: "narrator", text: response },
    ]);

    setHunger((previous) => Math.min(100, previous + 5));
    setInput("");
  }

  return (
    <div className={`screen-wrapper ${transitioning ? "fade-out" : "fade-in"}`}>

      {/* SCREEN 1: LANDING */}
      {screen === "landing" && (
        <main className="landing-page">
          <div className="landing-content">
            <h1>Whispers in the Dark</h1>

            <button
              className="wander-button"
              onClick={() => changeScreen("selection")}
            >
              Wander Around →
            </button>
          </div>
        </main>
      )}

      {/* SCREEN 2: WORLD SELECTION */}
      {screen === "selection" && (
        <main className="selection-page">
          <h1>Choose a Landing Place</h1>

          <div className="world-grid">
            {worlds.map((item) => (
              <button
                key={item.id}
                className={`world-card world-${item.id}`}
                onClick={() => startWorld(item)}
              >
                <span className="world-year">{item.year}</span>
                <h2>{item.name}</h2>
                <p>{item.theme}</p>
              </button>
            ))}
          </div>

          <button
            className="back-button"
            onClick={() => changeScreen("landing")}
          >
            ← Back
          </button>
        </main>
      )}

      {/* SCREEN 3: GAME */}
      {screen === "game" && world && (
        <main className="game-screen">
          <div className="game-container">

            <header className="game-header">
              <button
                className="back-button"
                onClick={() => changeScreen("selection")}
              >
                ← Back
              </button>

              <div className="game-heading">
                <span>{world.year}</span>
                <h1>{world.name}</h1>
              </div>
            </header>

            {/* Player survival stats */}
            <div className="survival-stats">
              <div className="stat">
                <div className="stat-heading">
                  <span>Health</span>
                  <span>{health}%</span>
                </div>

                <div className="stat-track">
                  <div
                    className="stat-fill health-fill"
                    style={{ width: `${health}%` }}
                  />
                </div>
              </div>

              <div className="stat">
                <div className="stat-heading">
                  <span>Hunger</span>
                  <span>{hunger}%</span>
                </div>

                <div className="stat-track">
                  <div
                    className="stat-fill hunger-fill"
                    style={{ width: `${hunger}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Story messages */}
            <section className="chat-panel">
              <div className="chat-messages">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`chat-message ${message.role}`}
                  >
                    {message.role === "player" && (
                      <span className="chat-label">YOU</span>
                    )}
                    <p>{message.text}</p>
                  </div>
                ))}
              </div>

              {/* Player input */}
              <form className="chat-form" onSubmit={handleAction}>
                <input
                  type="text"
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder="What do you do?"
                  aria-label="Your next action"
                />

                <button type="submit" disabled={!input.trim()}>
                  →
                </button>
              </form>
            </section>

          </div>
        </main>
      )}
    </div>
  );
}

export default App;

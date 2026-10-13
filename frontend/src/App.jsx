import { useEffect, useRef, useState } from "react";
import "./styles/app.css";

const API_URL = "http://127.0.0.1:8000";

const worlds = [
  { id: "hospital", name: "The Hospital", year: "1980", theme: "Zombie Apocalypse", opening: "You wake up in an abandoned hospital. The lights flicker above you. Somewhere down the corridor, you hear footsteps dragging across the floor." },
  { id: "forest", name: "The Forest", year: "1870", theme: "Europe", opening: "You wake on cold, wet soil. Ancient trees surround you. Moonlight passes through the branches. Something is watching from the darkness." },
  { id: "city", name: "The Last City", year: "2080", theme: "AI Apocalypse", opening: "The city has been silent for days. Drones patrol the empty streets. A mechanical voice whispers through a broken radio: We know you're here." },
];

// Use fictional clock fields directly; do not apply the browser's timezone.
function formatGameTime(timestamp) {
  if (!timestamp) return "";
  const [date, time] = timestamp.split("T");
  if (!date || !time) return "";
  const [year, month, day] = date.split("-");
  const [hour, minute] = time.split(":");
  const h = Number(hour);
  if (!Number.isFinite(h)) return "";
  return `${h % 12 || 12}:${minute} ${h >= 12 ? "PM" : "AM"} · ${month}/${day}/${year}`;
}

function TypewriterText({
  text,
  speed = 18,
  animate = false,
  showCursor = false,
  onProgress,
}) {
  const [visibleCount, setVisibleCount] = useState(
    animate ? 0 : text.length
  );

  useEffect(() => {
    if (!animate) {
      setVisibleCount(text.length);
      return;
    }

    let count = 0;
    setVisibleCount(0);

    const timer = setInterval(() => {
      count = Math.min(count + 1, text.length);
      setVisibleCount(count);
      onProgress?.();

      if (count >= text.length) {
        clearInterval(timer);
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed, animate]);

  return (
    <p>
      {text.slice(0, visibleCount)}
      {showCursor && (
        <span className="typewriter-cursor" aria-hidden="true">
          ▍
        </span>
      )}
    </p>
  );
}

function App() {
  const [screen, setScreen] = useState("landing");
  const [transitioning, setTransitioning] = useState(false);
  const [world, setWorld] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [health, setHealth] = useState(100);
  const [hunger, setHunger] = useState(0);
  const [sessionId, setSessionId] = useState(null);
  const [gameTime, setGameTime] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const chatRef = useRef(null);

  // Keep the latest story visible as new letters are revealed.
  const scrollToLatest = () => {
    const container = chatRef.current;
    if (container) container.scrollTop = container.scrollHeight;
  };

  useEffect(() => {
    scrollToLatest();
  }, [messages, loading]);

  function changeScreen(nextScreen, callback) {
    if (transitioning) return;
    setTransitioning(true);
    setTimeout(() => {
      if (callback) callback();
      setScreen(nextScreen);
      setTransitioning(false);
    }, 700);
  }

  async function startWorld(selectedWorld) {
    if (loading || transitioning) return;
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/game/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario_id: selectedWorld.id }),
      });
      if (!response.ok) throw new Error("Failed to start game. Check the backend.");
      const data = await response.json();
      changeScreen("game", () => {
        setWorld(selectedWorld);
        setSessionId(data.session_id);
        const startTime = data.response_time ?? data.world.game_time ?? null;
        setGameTime(startTime);
        setMessages([{ role: "narrator", text: selectedWorld.opening, timestamp: startTime }]);
        setHealth(data.world.health);
        setHunger(data.world.hunger);
        setInput("");
        setError("");
      });
    } catch (err) {
      setError(err.message || "Could not connect to the game server.");
    } finally {
      setLoading(false);
    }
  }

  async function handleAction(event) {
    event.preventDefault();
    const action = input.trim();
    if (!action || !sessionId || loading || transitioning) return;

    const actionTime = gameTime;
    setLoading(true);
    setError("");
    setMessages((previous) => [...previous, { role: "player", text: action, timestamp: actionTime }]);
    setInput("");

    try {
      const response = await fetch(`${API_URL}/game/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, action }),
      });
      if (!response.ok) {
        const details = await response.json().catch(() => null);
        throw new Error(details?.detail || "Failed to process action. Please try again.");
      }

      const data = await response.json();
      const responseTime = data.response_time ?? data.world.game_time ?? actionTime;
      setMessages((previous) => [
        ...previous,
        { role: "narrator", text: data.narration, timestamp: responseTime },
      ]);
      setGameTime(responseTime);
      setHealth(data.world.health);
      setHunger(data.world.hunger);
    } catch (err) {
      setError(err.message || "Could not contact the game server.");
      setInput(action);
      setMessages((previous) => previous.slice(0, -1));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={`screen-wrapper ${transitioning ? "fade-out" : "fade-in"}`}>
      <style>{`
        .typewriter-cursor {
          display: inline-block;
          margin-left: 2px;
          color: #a8c9b2;
          animation: whisper-cursor-blink 1.05s ease-in-out infinite;
        }
        @keyframes whisper-cursor-blink {
          0%, 100% { opacity: 0.95; }
          50% { opacity: 0.08; }
        }
        /* Thin, dark scrollbar instead of the browser's white scrollbar. */
        .chat-messages {
          scrollbar-width: thin;
          scrollbar-color: #496656 #101b16;
          scroll-behavior: auto;
          overscroll-behavior: contain;
        }
        .chat-messages::-webkit-scrollbar { width: 7px; }
        .chat-messages::-webkit-scrollbar-track { background: #101b16; }
        .chat-messages::-webkit-scrollbar-thumb {
          background: #496656;
          border-radius: 12px;
        }
        .chat-messages::-webkit-scrollbar-thumb:hover { background: #759281; }
        .message-timestamp {
          display: block;
          margin-top: 6px;
          font-size: 10px;
          opacity: 0.48;
          letter-spacing: 0.4px;
          font-variant-numeric: tabular-nums;
        }
        .chat-message.player .message-timestamp { text-align: right; }
        @media (prefers-reduced-motion: reduce) {
          .typewriter-cursor { animation: none; }
        }
      `}</style>

      {screen === "landing" && (
        <main className="landing-page">
          <div className="landing-content">
            <h1>Whispers in the Dark</h1>
            <button className="wander-button" onClick={() => changeScreen("selection")}>Wander Around →</button>
          </div>
        </main>
      )}

      {screen === "selection" && (
        <main className="selection-page">
          <h1>Choose a Landing Place</h1>
          <div className="world-grid">
            {worlds.map((item) => (
              <button key={item.id} className={`world-card world-${item.id}`} onClick={() => startWorld(item)} disabled={loading || transitioning}>
                <span className="world-year">{item.year}</span>
                <h2>{item.name}</h2>
                <p>{item.theme}</p>
              </button>
            ))}
          </div>
          {loading && <p aria-live="polite">Entering the darkness...</p>}
          {error && <p role="alert">{error}</p>}
          <button className="back-button" disabled={loading || transitioning} onClick={() => changeScreen("landing")}>← Back</button>
        </main>
      )}

      {screen === "game" && world && (
        <main className="game-screen">
          <div className="game-container">
            <header className="game-header">
              <button className="back-button" disabled={loading || transitioning} onClick={() => changeScreen("selection")}>← Back</button>
              <div className="game-heading"><span>{world.year}</span><h1>{world.name}</h1></div>
            </header>
            <div className="survival-stats">
              <div className="stat">
                <div className="stat-heading"><span>Health</span><span>{health}%</span></div>
                <div className="stat-track"><div className="stat-fill health-fill" style={{ width: `${health}%` }} /></div>
              </div>
              <div className="stat">
                <div className="stat-heading"><span>Hunger</span><span>{hunger}%</span></div>
                <div className="stat-track"><div className="stat-fill hunger-fill" style={{ width: `${hunger}%` }} /></div>
              </div>
            </div>
            <section className="chat-panel">
              <div className="chat-messages" ref={chatRef} aria-live="polite">
                {messages.map((message, index) => (
                  <div key={index} className={`chat-message ${message.role}`}>
                    {message.role === "narrator" ? (
                      <TypewriterText text={message.text} animate={index === messages.length - 1 && message.role === "narrator"} showCursor={index === messages.length - 1 && message.role === "narrator" } onProgress={scrollToLatest} />
                    ) : (
                      <p>{message.text}</p>
                    )}
                    {message.timestamp && (
                      <span className="message-timestamp">{formatGameTime(message.timestamp)}</span>
                    )}
                  </div>
                ))}
              </div>
              {loading && <p className="loading-message" aria-live="polite">The world is responding...</p>}
              {error && <p role="alert">{error}</p>}
              <form className="chat-form" onSubmit={handleAction}>
                <input type="text" value={input} onChange={(event) => setInput(event.target.value)} placeholder="What do you do?" aria-label="Your next action" disabled={loading} />
                <button type="submit" disabled={!input.trim() || loading || !sessionId || transitioning}>→</button>
              </form>
            </section>
          </div>
        </main>
      )}
    </div>
  );
}

export default App;


import { useState } from "react";

import Header from "./components/Header";
import StoryPanel from "./components/StoryPanel";
import ActionInput from "./components/ActionInput";
import SidePanel from "./components/SidePanel";

import "./styles/app.css";

function App() {
  const [screen, setScreen] = useState("landing");

  const [messages, setMessages] = useState([
    {
      type: "system",
      text: "You wake on cold, wet soil. Pines stand around you, black against a pale moon. Somewhere beyond the trees, a branch snaps.",
    },
  ]);

  const [gameState, setGameState] = useState({
    location: "Forest",
    threatLevel: 2,
    condition: "Stable",
    inventory: ["Old Note"],
  });

  function startGame() {
    if (screen !== "landing") return;

    setScreen("leaving");

    setTimeout(() => {
      setScreen("game");
    }, 900);
  }

  function handleAction(action) {
    const trimmedAction = action.trim();

    if (!trimmedAction) return;

    const lowerAction = trimmedAction.toLowerCase();

    let response =
      "The forest listens. Somewhere in the darkness, leaves begin to move.";

    if (lowerAction.includes("look")) {
      response =
        "Moonlight filters through the trees. You notice a narrow path and a loose rock near your feet.";
    } else if (lowerAction.includes("wait")) {
      response =
        "You remain still. The forest grows quieter. Something is breathing nearby.";
    } else if (lowerAction.includes("rock")) {
      response =
        "You pick up the cold rock. It feels heavy in your hand.";

      setGameState((prev) => ({
        ...prev,
        inventory: prev.inventory.includes("Rock")
          ? prev.inventory
          : [...prev.inventory, "Rock"],
      }));
    } else if (lowerAction.includes("run")) {
      response =
        "You run between the trees. Behind you, footsteps begin matching your pace.";
    }

    setMessages((prev) => [
      ...prev,
      { type: "player", text: trimmedAction },
      { type: "system", text: response },
    ]);

    setGameState((prev) => ({
      ...prev,
      threatLevel: Math.min(prev.threatLevel + 1, 10),
    }));
  }

  if (screen !== "game") {
    return (
      <main
        className={`landing-page ${
          screen === "leaving" ? "fade-out" : ""
        }`}
      >
        <div className="landing-content">
          <h1>Whispers in the Dark</h1>

          <button
            className="wander-button"
            onClick={startGame}
            disabled={screen === "leaving"}
          >
            Wander Around <span aria-hidden="true">→</span>
          </button>
        </div>
      </main>
    );
  }

  return (
    <div className="app-shell game-fade-in">
      <div className="background-glow" />

      <Header />

      <main className="game-layout">
        <section className="left-column">
          <StoryPanel messages={messages} />
          <ActionInput onSubmit={handleAction} />
        </section>

        <aside className="right-column">
          <SidePanel gameState={gameState} />
        </aside>
      </main>
    </div>
  );
}

export default App;

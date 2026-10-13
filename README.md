# Whispers in the Dark

**An AI-powered, open-ended survival-horror text adventure.**

*The world does not wait for you.*

Whispers in the Dark is an experimental, single-player narrative game in which players type actions in natural language rather than choose from a fixed menu. A language model interprets their intentions and proposes discoveries; a Python game engine manages persistent objects, inventory, game time, and events.

> **Status: Playable alpha / pre-MVP.** The React frontend, FastAPI gameplay API, OpenAI integration, and SQLite-backed sessions work locally. Movement, physical interactions, event causality, and full save/resume are still under development. This is not a finished survival simulator.

## Gameplay

Choose one of three starting scenarios:

| Scenario | Year | Setting |
| --- | --- | --- |
| **The Hospital** | 1980 | Zombie-apocalypse horror in an abandoned hospital |
| **The Forest** | 1870 | Gothic horror in a fog-covered European forest |
| **The Last City** | 2080 | AI-apocalypse survival in an abandoned city |

Describe what you want to do: inspect a room, search beneath furniture, take an item, or attempt something unexpected. Actions can fail; the long-term design principle is **freedom to attempt, not guaranteed success**.

The interface deliberately stays minimal: a story feed, free-text input, health and hunger indicators, and timestamps from the fictional world clock. Narration uses a gradual typewriter effect and restrained horror prose.

## Implemented features

- **Natural-language gameplay:** an OpenAI-backed `WorldDirector` produces Pydantic-structured proposals.
- **Three scenario configurations:** separate JSON-defined settings, eras, threats, and rules.
- **Persistent world state:** SQLite sessions store scenario, current position fields, game time, objects, inventory references, flags, and event history.
- **Seeded environment:** the Hospital starts with established items, including visible and hidden objects.
- **Basic validated interactions:** the engine supports pickup, drop, and inspect operations for referenced objects.
- **Location graph foundation:** SQLite tables model locations and directed, potentially locked connections.
- **World clock:** action durations advance fictional time, including overnight date changes; messages display the action's start time and the response's end time.
- **Timeline prototype:** scenario-specific scheduled events can mutate state based on flags; scheduling is currently **turn-based**, not clock-based.
- **Atmospheric React UI:** scenario selection, fade transitions, typewriter narration, blinking cursor, compact timestamps, and chat scrolling.

### Current limitations

The AI may still *describe* actions that the Python engine does not execute. In particular:

- Players cannot yet reliably navigate rooms via the location graph.
- Hidden-object visibility and discovery are not fully enforced by the resolver.
- Breaking, repairing, unlocking, fighting, and other physical consequences lack generalized validation.
- Sleeping advances the clock, but scheduled events cannot yet interrupt it; timeline triggers still use turns.
- NPC behavior, active survival rules, death conditions, and complete narrative memory are not yet implemented.
- Session data persists in SQLite, but the browser does not yet provide a complete save/resume experience with restored dialogue.

## Tech stack

| Layer | Technology |
| --- | --- |
| Frontend | React, JavaScript, Vite, CSS |
| Backend API | Python, FastAPI |
| AI | OpenAI Responses API, Pydantic structured outputs |
| Game engine | Python world state, operations, clock, and timeline modules |
| Persistence | SQLite (`sqlite3`) |
| Tooling | `uv`, npm, pytest |

## Architecture

```text
Player action (React)
        |
        v
POST /game/action (FastAPI)
        |
        v
Load session + scenario (SQLite / JSON)
        |
        v
WorldDirector: narration + structured proposals (OpenAI)
        |
        v
Apply discoveries + resolve supported object operations (Python)
        |
        v
Advance game clock + process timeline (Python)
        |
        v
Save WorldState (SQLite)
        |
        v
Narration + updated stats + timestamps (React)
```

**Engineering direction:** In the current alpha, the director generates narration before all effects have been validated. A planned separation of **intent interpretation → authoritative rule resolution → perceptual narration** will make the narrative match actual world changes.

### Project structure

```text
whispers-in-the-dark/
├── frontend/
│   └── src/
│       ├── App.jsx                  # Screens, story feed, API calls
│       └── styles/app.css           # Visual styling
└── backend/
    ├── app/
    │   ├── main.py                  # FastAPI app and CORS
    │   ├── api/game.py              # Gameplay endpoints
    │   ├── ai/director.py           # Structured LLM proposals
    │   ├── engine/
    │   │   ├── world.py              # Load scenarios / create worlds
    │   │   ├── seeding.py            # Starting environment
    │   │   ├── mutations.py          # Object discovery proposals
    │   │   ├── actions.py            # Pickup / drop / inspect
    │   │   ├── clock.py              # Fictional time and durations
    │   │   └── timeline.py           # Prototype scheduled events
    │   ├── models/schemas.py        # Pydantic models
    │   ├── scenarios/               # Scenario and timeline JSON
    │   └── storage/
    │       ├── database.py          # SQLite schema / connections
    │       ├── graph.py             # Locations and connections
    │       └── sessions.py          # Session persistence
    ├── tests/                        # Pytest checks
    └── pyproject.toml                # Python dependencies
```

## Run locally

### Requirements

- Python **3.11+** (development has used Python 3.12)
- [uv](https://docs.astral.sh/uv/)
- Node.js and npm compatible with the project's Vite version
- An OpenAI API key with available API billing/credits (billed separately from ChatGPT)

### 1. Clone and configure the backend

```bash
git clone https://github.com/Tarikdycl/whispers-in-the-dark.git
cd whispers-in-the-dark/backend
uv sync
```

Create a **private** `backend/.env` file:

```dotenv
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4.1-mini
```

Never commit `.env` or publish your API key. The model shown is an example configuration; availability and costs depend on your API account.

Launch FastAPI:

```bash
uv run uvicorn app.main:app --reload
```

Backend: **http://127.0.0.1:8000**  
Interactive API docs: **http://127.0.0.1:8000/docs**

### 2. Start the frontend

Open a second terminal from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** and choose a scenario. Both servers need to be running. The frontend currently uses a local backend URL, so production deployment will require API URL configuration and appropriate CORS settings.

### 3. Run tests

From `backend/`:

```bash
uv run python -m pytest -v
```

The test suite covers foundational scenario, world, storage, graph, and mutation behavior. Newer AI interaction and clock features need additional regression tests. Routine unit tests should mock LLM calls rather than incur API charges.

## Gameplay API

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/game/start` | Start a new scenario and return its session ID |
| `POST` | `/game/action` | Submit an action and receive narration, timestamps, and updated state |
| `GET` | `/game/{session_id}` | Read the saved world state |

Example request:

```json
{
  "session_id": "your-session-id",
  "action": "I search underneath the hospital bed."
}
```

## Roadmap

### Toward the single-player MVP

- [x] Responsive horror UI and scenario selection
- [x] OpenAI structured response integration
- [x] SQLite world-state persistence
- [x] Basic object interactions and starting environment
- [x] Fictional clock and message timestamps
- [ ] Authoritative room navigation and visibility/discovery rules
- [ ] Validated physical actions and consequence handling
- [ ] Time-based events, interrupts, and perception-aware narration
- [ ] Basic NPC threats, survival mechanics, and game-over conditions
- [ ] Browser save/resume with persistent dialogue
- [ ] Security, API cost controls, regression tests, and deployment

### Longer-term vision (not in the MVP)

- **Custom scenarios:** author or generate settings, eras, locations, and core timelines (for example, a haunted farmhouse in 1930s Tennessee).
- **Shared-world multiplayer:** players occupy the same timeline and locations, witnessing each other's actions when perception allows.
- **Emergent social simulation:** relationships, families, factions, settlements, and evolving societies.
- **Provider flexibility:** evaluate local/open-weight models and reduce inference cost.

The goal is to let players **attempt virtually anything**, while a consistent world simulation determines what actually happens.

## Project status

**Experimental alpha.** Built as an independent full-stack AI engineering and game-development project. Gameplay systems and APIs may change as the simulation engine evolves.

\# Whispers in the Dark



\*An AI-powered interactive psychological horror adventure.\*



\*\*Whispers in the Dark\*\* is an experimental narrative horror game where players interact with a mysterious world through natural language. Instead of selecting from predefined choices, players describe their actions freely, while an AI narrator interprets their intentions and tells the evolving story.



> The darkness is listening. What will you do?



\## The Concept



You awaken in an unfamiliar place. You don't know where you are, what happened, or what might be watching you.



You can look around, explore, hide, interact with objects, or attempt almost anything you can describe.



The world responds to your decisions. Every action may reveal information, change your surroundings, or bring something closer.



\## Planned Features



\- \*\*Free-form interaction:\*\* Describe actions in natural language.

\- \*\*AI-powered narration:\*\* An LLM generates atmospheric, context-aware responses.

\- \*\*Persistent game state:\*\* Locations, inventory, discoveries, and consequences remain consistent.

\- \*\*Dynamic horror:\*\* Threats and events evolve based on player behavior.

\- \*\*Multiple scenarios:\*\* Different locations, timelines, stories, and endings.

\- \*\*Minimalist interface:\*\* An immersive, text-first experience with atmospheric visual and audio design.



\## Technology Stack



| Layer | Technology |

|---|---|

| Frontend | React, Vite, JavaScript |

| Backend | Python, FastAPI |

| Package Management | npm, uv |

| AI Narration | LLM integration (planned) |

| Game Logic | Python-based state and rules engine (planned) |



\## Getting Started



\### Requirements



\- Node.js and npm

\- Python 3.12

\- uv



\### Frontend



```bash

cd frontend

npm install

npm run dev

```



\### Backend



Open another terminal:



```bash

cd backend

uv sync

uv run uvicorn app.main:app --reload

```



Frontend: `http://localhost:5173`



Backend API documentation: `http://127.0.0.1:8000/docs`



\## Roadmap



\- \[x] Initialize React frontend

\- \[x] Configure Python backend with FastAPI and uv

\- \[x] Run the initial development servers

\- \[ ] Design the core game state and action system

\- \[ ] Connect frontend and backend

\- \[ ] Integrate an LLM narrator

\- \[ ] Build the first playable horror scenario

\- \[ ] Implement inventory, memory, and branching outcomes

\- \[ ] Add immersive UI animations and sound

\- \[ ] Playtest and prepare a public demo



\## Project Status



\*\*Early development — Pre-alpha\*\*



The initial development environment and API are set up. Gameplay and AI narration are not yet implemented.



\## Vision



The goal is to create a replayable horror experience where the player's imagination becomes the interface, and the game world reacts meaningfully to their choices.



Built as an independent game development and AI engineering project.


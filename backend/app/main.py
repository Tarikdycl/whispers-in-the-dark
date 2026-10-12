from fastapi import FastAPI
from app.api.game import router as game_router

app = FastAPI(title="Whispers in the Dark API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(game_router)


@app.get("/")
def home():
    return {"message": "Welcome to Whispers in the Dark"}

@app.get("/health")
def health():
    return {"status": "running"}


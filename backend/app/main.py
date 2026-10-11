from fastapi import FastAPI

app = FastAPI(title="Whispers in the Dark API")

@app.get("/")
def home():
    return {"message": "Welcome to Whispers in the Dark"}

@app.get("/health")
def health():
    return {"status": "running"}
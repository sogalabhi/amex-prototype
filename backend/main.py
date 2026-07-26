from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv()

from api.routes import router

app = FastAPI(
    title="Verdict Chain",
    description="AI-powered dispute resolution with deterministic rules and tamper-evident audit trails",
    version="0.1.0",
)

# CORS - allow Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "name": "Verdict Chain",
        "status": "running",
        "docs": "/docs",
    }

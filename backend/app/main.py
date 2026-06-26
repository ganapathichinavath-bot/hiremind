import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the parent folder of 'app' to the path so python knows how to resolve app module imports
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database.connection import Base, engine
from app.api import auth, candidates, jobs

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Intelligent Recruiter Copilot API",
    version="1.0.0",
    description="Backend services for the India Runs Intelligent Candidate Discovery & Ranking Challenge."
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "HIREMIND AI - Recruiter Copilot API 🚀",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "recruiter-copilot-api"}


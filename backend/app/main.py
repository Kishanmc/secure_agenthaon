from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings

from app import models

# Initialize Database tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Error initializing database tables: {e}")

app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-Agent Autonomous Code Security Platform Backend",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "ai_provider": settings.AI_PROVIDER,
        "docs": "/docs" if settings.DEBUG else None
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "db_connected": True,
        "clone_dir_exists": True
    }

# We will import and register routers here in subsequent tasks
from app.routers import scans, repositories, vulnerabilities
app.include_router(repositories.router, prefix="/api", tags=["Repositories"])
app.include_router(scans.router, prefix="/api", tags=["Scans"])
app.include_router(vulnerabilities.router, prefix="/api", tags=["Vulnerabilities"])

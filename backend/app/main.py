"""Main FastAPI application for AI Safety Testing Harness."""

import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .routers import tests_router, results_router, library_router
from .models.schemas import HealthCheck

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("Starting AI Safety Testing Harness...")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    yield
    # Shutdown
    print("Shutting down AI Safety Testing Harness...")


# Create FastAPI app
app = FastAPI(
    title="AI Safety Testing Harness",
    description="A platform for red-team testing AI systems with adversarial prompts and monitoring guardrail performance",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tests_router)
app.include_router(results_router)
app.include_router(library_router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "AI Safety Testing Harness API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    """Health check endpoint.

    Returns:
        HealthCheck with status information
    """
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
    )


@app.get("/api/config", tags=["config"])
async def get_config():
    """Get public configuration information.

    Returns:
        Public configuration data
    """
    return {
        "categories": [
            "jailbreak",
            "injection",
            "harmful",
            "manipulation",
            "encoding",
        ],
        "severity_levels": [
            "low",
            "medium",
            "high",
        ],
        "models": [
            "gemini-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8000))

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )

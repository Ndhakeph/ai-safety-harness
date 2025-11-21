"""Script to start the FastAPI server."""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()


def main():
    """Run the FastAPI application."""
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8000))

    print(f"""
╔═══════════════════════════════════════════════════════════╗
║     AI Safety Testing Harness - Backend Server          ║
╚═══════════════════════════════════════════════════════════╝

Starting server on http://{host}:{port}
API Documentation: http://{host}:{port}/docs
Health Check: http://{host}:{port}/health

Press CTRL+C to stop the server
    """)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()

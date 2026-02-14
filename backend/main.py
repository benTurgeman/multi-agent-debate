"""Multi-Agent Debate Engine - FastAPI Backend."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import debates, providers, websocket
from routers.debates import get_debate_manager
from routers.websocket import setup_websocket_broadcasting

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown)."""
    # Startup
    logger.info("Starting Multi-Agent Debate Engine backend")

    # Set up WebSocket broadcasting
    debate_manager = get_debate_manager()
    setup_websocket_broadcasting(debate_manager)

    logger.info("WebSocket broadcasting configured")

    yield

    # Shutdown
    logger.info("Shutting down Multi-Agent Debate Engine backend")


# Create FastAPI app
app = FastAPI(
    title="Multi-Agent Debate Engine",
    description="Backend API for orchestrating multi-agent AI debates",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev port
        "http://localhost:3000",  # Alternative frontend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "Multi-Agent Debate Engine"}


# Mount routers
app.include_router(debates.router)
app.include_router(providers.router)
app.include_router(websocket.router)

logger.info("Routers mounted successfully")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

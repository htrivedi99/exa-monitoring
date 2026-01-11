from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.api.routes import monitors, results
from app.scheduler.background import scheduler

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting up application...")
    scheduler.start()
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    scheduler.shutdown()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Exa Monitor API",
    description="Monitor the internet for new content using Exa AI",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(monitors.router, prefix="/api/v1")
app.include_router(results.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "ok",
        "message": "Exa Monitor API is running"
    }


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Exa Monitor API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

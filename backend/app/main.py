"""FastAPI entry point for ARIA."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.connection import init_db
from app.api.routes import chat, trading, research, feedback
from app.utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    setup_logging()
    logging.info("Starting ARIA - Adaptive Research & Intelligence Agent")
    await init_db()
    logging.info("Database initialized")
    yield
    # Shutdown
    logging.info("Shutting down ARIA")


app = FastAPI(
    title=settings.app_name,
    description="Adaptive Research & Intelligence Agent - A fully local AI assistant",
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS middleware
origins = [origin.strip() for origin in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])
app.include_router(research.router, prefix="/api/research", tags=["Research"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "message": "Welcome to ARIA - Adaptive Research & Intelligence Agent",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}

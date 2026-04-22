from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.routers import tryon
from app.utils.rate_limiter import setup_rate_limiter
from app.utils.logging_config import setup_logging
from config.settings import settings

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info("Starting AI Hairstyle Service...")
    logger.info(f"Configuration loaded: AI Model={settings.gemini_model}, Workers={settings.workers}")
    logger.info(f"API will be available at http://{settings.api_host}:{settings.api_port}")
    yield
    logger.info("Shutting down AI Hairstyle Service...")

# Create FastAPI application
app = FastAPI(
    title="AI Hairstyle Try-On Service",
    description="Production-ready API for applying hairstyles using Google Gemini AI",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure rate limiter
setup_rate_limiter(app)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure specific hosts in production
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tryon.router)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "AI Hairstyle Try-On",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/v1/health",
        "endpoints": {
            "POST /api/v1/try-on": "Apply a new hairstyle to an image",
            "GET /api/v1/health": "Health check"
        }
    }

@app.get("/api/v1/health")
async def global_health_check():
    """Global health check endpoint."""
    return {"status": "healthy", "service": "ai-hairstyle", "version": "1.0.0"}
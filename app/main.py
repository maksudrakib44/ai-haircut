from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.routers import tryon
from app.utils.rate_limiter import setup_rate_limiter
from app.utils.logging_config import setup_logging
from config.settings import settings

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Hairstyle Service v2.0 (Batch Support)")
    logger.info(f"Model: {settings.gemini_model}, Workers: {settings.workers}")
    yield
    logger.info("Shutting down")

app = FastAPI(
    title="AI Hairstyle Try-On Service",
    description="Single and batch hairstyle generation using Gemini 3.1 Flash Image",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

setup_rate_limiter(app)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tryon.router)

@app.get("/")
async def root():
    return {
        "service": "AI Hairstyle Try-On",
        "version": "2.0.0",
        "endpoints": {
            "POST /api/v1/try-on": "Single hairstyle",
            "POST /api/v1/try-on-batch": "Multiple hairstyles (Short, Medium, Long, etc.)",
            "GET /api/v1/health": "Health check"
        },
        "docs": "/docs"
    }
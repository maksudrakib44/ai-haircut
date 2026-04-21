from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class TryOnRequest(BaseModel):
    """Request model for hairstyle transformation."""
    style: str = Field(..., min_length=1, max_length=100, description="Desired hairstyle description")
    
    @validator('style')
    def validate_style(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Hairstyle description cannot be empty')
        return v.strip()

class TryOnResponse(BaseModel):
    """Response model for hairstyle transformation."""
    success: bool
    message: str
    image_base64: Optional[str] = None
    processing_time_ms: Optional[float] = None

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str
    timestamp: datetime

class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str
    error_code: str
    timestamp: datetime
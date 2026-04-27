from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class TryOnRequest(BaseModel):
    style: str = Field(..., min_length=1, max_length=100, description="Hairstyle description")
    
    @validator('style')
    def validate_style(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Hairstyle description cannot be empty')
        return v.strip()

class TryOnResponse(BaseModel):
    success: bool
    message: str
    image_base64: Optional[str] = None
    processing_time_ms: Optional[float] = None

class BatchTryOnRequest(BaseModel):
    styles: List[str] = Field(..., description="List of hairstyle descriptions or category keys")
    
    @validator('styles')
    def validate_styles(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError('At least one style is required')
        if len(v) > 6:
            raise ValueError('Maximum 6 styles per request')
        return [s.strip() for s in v if s.strip()]

class GeneratedImage(BaseModel):
    style_key: str
    style_description: str
    image_base64: str
    mime_type: str = "image/jpeg"

class BatchTryOnResponse(BaseModel):
    success: bool
    message: str
    generated_images: List[GeneratedImage]
    total_processing_time_ms: float

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime

class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: datetime
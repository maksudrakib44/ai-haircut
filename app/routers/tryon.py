from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address
import time
from loguru import logger

from app.services.gemini_client import GeminiClient
from app.utils.validators import validate_image
from config.settings import settings

router = APIRouter(prefix="/api/v1", tags=["hairstyle"])

# Rate limiter for this router
limiter = Limiter(key_func=get_remote_address)

# Singleton Gemini client
_gemini_client = None

def get_gemini_client() -> GeminiClient:
    """Dependency injection for Gemini client."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client

@router.post(
    "/try-on",
    responses={
        200: {"description": "Successfully generated image", "content": {"image/jpeg": {}}},
        400: {"description": "Bad request"},
        429: {"description": "Rate limit exceeded"},
        502: {"description": "AI service error"}
    }
)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def try_on_hairstyle(
    image: UploadFile = File(..., description="User selfie image (JPEG or PNG, max 5MB)"),
    style: str = Form(..., description="Desired hairstyle description (e.g., 'long curly red hair')"),
    request = None,
    gemini_client: GeminiClient = Depends(get_gemini_client)
):
    """
    Apply a new hairstyle to the uploaded image using Gemini AI.
    
    - **image**: JPEG or PNG file, maximum 5MB
    - **style**: Text description of the desired hairstyle
    
    Returns the generated image as a JPEG file.
    """
    start_time = time.time()
    
    # Log request
    client_ip = request.client.host if request else "unknown"
    logger.info(f"Try-on request from {client_ip} for style: {style}")
    
    try:
        # Validate and read image
        image_bytes = await validate_image(image)
        logger.debug(f"Image validated: {image.filename}, {len(image_bytes)} bytes")
        
        # Call Gemini AI
        result_bytes = await gemini_client.generate_hairstyle(image_bytes, style)
        
        # Log processing time
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"Try-on completed in {elapsed_ms:.2f}ms")
        
        # Return image directly
        return Response(
            content=result_bytes,
            media_type="image/jpeg",
            headers={
                "X-Processing-Time-Ms": str(int(elapsed_ms)),
                "Cache-Control": "no-cache"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except RuntimeError as e:
        # Gemini API errors
        logger.error(f"AI service error: {str(e)}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        # Unexpected errors
        logger.exception(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "ai-hairstyle", "version": "1.0.0"}
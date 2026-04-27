from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address
import time
import json
from loguru import logger

from app.services.gemini_client import GeminiClient
from app.utils.validators import validate_image
from app.models.schemas import BatchTryOnResponse, GeneratedImage
from config.settings import settings

router = APIRouter(prefix="/api/v1", tags=["hairstyle"])
limiter = Limiter(key_func=get_remote_address)

_gemini_client = None

def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client

def map_ui_category_to_prompt(category: str) -> str:
    """Convert UI category (short, medium, long) to full prompt."""
    category_lower = category.lower().strip()
    if category_lower in settings.hairstyle_categories:
        return settings.hairstyle_categories[category_lower]
    return category

@router.post("/try-on")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def try_on_hairstyle(
    request: Request,
    image: UploadFile = File(...),
    style: str = Form(...),
    gemini_client: GeminiClient = Depends(get_gemini_client)
):
    """Single hairstyle generation."""
    start_time = time.time()
    logger.info(f"Single try-on for style: {style}")
    
    try:
        image_bytes = await validate_image(image)
        result_bytes = await gemini_client.generate_hairstyle(image_bytes, style)
        elapsed_ms = (time.time() - start_time) * 1000
        return Response(
            content=result_bytes,
            media_type="image/jpeg",
            headers={"X-Processing-Time-Ms": str(int(elapsed_ms))}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/try-on-batch")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def try_on_hairstyle_batch(
    request: Request,
    image: UploadFile = File(...),
    styles: str = Form(...),
    gemini_client: GeminiClient = Depends(get_gemini_client)
):
    """
    Generate multiple hairstyles in one request.
    
    - styles: can be a JSON array, e.g., '["short","medium","long"]'
             OR a comma-separated string, e.g., 'short,medium,long'
    """
    total_start = time.time()
    
    try:
        styles = styles.strip()
        
        # Parse styles: try JSON first, fallback to comma-separated
        if styles.startswith('['):
            style_list = json.loads(styles)
        else:
            # Split by comma and clean each item
            style_list = [s.strip() for s in styles.split(',') if s.strip()]
        
        if not isinstance(style_list, list) or not style_list:
            raise HTTPException(status_code=400, detail="styles must be a non-empty JSON array or comma-separated list")
        
        if len(style_list) > 6:
            raise HTTPException(status_code=400, detail="Maximum 6 styles per request")
        
        # Map UI categories to prompts
        mapped_styles = []
        for s in style_list:
            prompt = map_ui_category_to_prompt(s)
            mapped_styles.append({"key": s, "description": prompt})
        
        logger.info(f"Batch request for {len(mapped_styles)} styles: {style_list}")
        
        image_bytes = await validate_image(image)
        results = await gemini_client.generate_multiple_hairstyles(image_bytes, mapped_styles)
        
        total_elapsed = (time.time() - total_start) * 1000
        
        generated_images = [
            GeneratedImage(
                style_key=item['style_key'],
                style_description=item['style_description'],
                image_base64=item['image_base64'],
                mime_type=item['mime_type']
            )
            for item in results
        ]
        
        return BatchTryOnResponse(
            success=True,
            message=f"Generated {len(generated_images)} hairstyles",
            generated_images=generated_images,
            total_processing_time_ms=total_elapsed
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in styles field")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch error: {str(e)}")
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-hairstyle", "version": "2.0.0"}
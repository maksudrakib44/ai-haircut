import google.generativeai as genai
from PIL import Image
import io
import time
from loguru import logger
from config.settings import settings

class GeminiClient:
    """Client for Google Gemini AI image editing."""
    
    def __init__(self):
        """Initialize Gemini client with API key and model configuration."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        logger.info(f"Gemini client initialized with model: {settings.gemini_model}")
    
    async def generate_hairstyle(self, image_bytes: bytes, style: str) -> bytes:
        """
        Send image and style prompt to Gemini, return generated image bytes.
        
        Args:
            image_bytes: Raw image bytes from uploaded file
            style: Hairstyle description string
            
        Returns:
            Generated image bytes in JPEG format
            
        Raises:
            RuntimeError: If Gemini API returns an error or no image data
        """
        start_time = time.time()
        
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_bytes))
            logger.debug(f"Image opened successfully. Size: {image.size}, Mode: {image.mode}")
            
            # Build prompt with style
            prompt = settings.hairstyle_prompt_template.format(style=style)
            logger.debug(f"Generated prompt: {prompt[:100]}...")
            
            # Call Gemini API
            logger.info("Calling Gemini API for image generation...")
            response = self.model.generate_content([prompt, image])
            
            # Check if response contains image data
            if not response.candidates:
                logger.error("No candidates returned from Gemini API")
                raise RuntimeError("No candidates returned from Gemini API")
            
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                logger.error("No content parts in Gemini response")
                raise RuntimeError("No image data in Gemini response")
            
            # Extract image data
            image_data = None
            for part in candidate.content.parts:
                # Check for inline image data
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data
                    break
                # Check for text that might contain a URL or base64
                elif hasattr(part, 'text') and part.text:
                    logger.debug(f"Gemini returned text: {part.text[:200]}")
                    # If text contains a URL, we could fetch it, but Gemini 1.5 Pro may not output images directly
                    # For now, raise error
                    raise RuntimeError(f"Gemini returned text instead of image: {part.text[:100]}")
            
            if not image_data:
                logger.error("No image data found in Gemini response")
                raise RuntimeError("No image data received from Gemini")
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Gemini API call completed in {elapsed:.2f}ms")
            
            return image_data
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise RuntimeError(f"AI service error: {str(e)}")
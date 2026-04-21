import google.generativeai as genai
from PIL import Image
import io
import time
from loguru import logger
from config.settings import settings

class GeminiClient:
    """Client for Google Gemini AI image generation (text-to-image with image input)."""
    
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
            
            # Call Gemini API with response_modalities to request image output
            logger.info("Calling Gemini API for image generation...")
            response = self.model.generate_content(
                [prompt, image],
                generation_config=genai.types.GenerationConfig(
                    response_modalities=['IMAGE']
                )
            )
            
            # Extract generated image data
            if not response.candidates:
                logger.error("No candidates returned from Gemini API")
                raise RuntimeError("No candidates returned from Gemini API")
            
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                logger.error("No content parts in Gemini response")
                raise RuntimeError("No image data in Gemini response")
            
            # Find the part that contains image data
            image_data = None
            for part in candidate.content.parts:
                if part.inline_data and part.inline_data.data:
                    image_data = part.inline_data.data
                    break
            
            if not image_data:
                logger.error("No inline image data found in Gemini response")
                raise RuntimeError("No image data received from Gemini")
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Gemini API call completed in {elapsed:.2f}ms")
            
            return image_data
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise RuntimeError(f"AI service error: {str(e)}")
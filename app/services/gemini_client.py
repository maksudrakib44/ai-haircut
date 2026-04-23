import google.generativeai as genai
from PIL import Image
import io
import time
import base64
import re
from loguru import logger
from config.settings import settings

class GeminiClient:
    """Client for Google Gemini 3.1 Flash Image AI image editing."""
    
    def __init__(self):
        """Initialize Gemini client with API key and model configuration."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        logger.info(f"Gemini client initialized with model: {settings.gemini_model}")
    
    async def generate_hairstyle(self, image_bytes: bytes, style: str) -> bytes:
        """
        Send image and style prompt to Gemini 3.1 Flash Image, return generated image bytes.
        
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
            logger.info("Calling Gemini 3.1 Flash Image API...")
            
            # Try different generation config approaches
            try:
                # Attempt 1: With generation config for image output
                generation_config = genai.types.GenerationConfig(
                    temperature=1.0,
                    top_p=0.95,
                    top_k=40,
                    candidate_count=1,
                )
                response = self.model.generate_content(
                    [prompt, image],
                    generation_config=generation_config
                )
            except TypeError:
                # Attempt 2: Without generation config
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
                    logger.debug("Found inline image data")
                    break
                # Check for text that might contain image
                elif hasattr(part, 'text') and part.text:
                    text = part.text
                    logger.debug(f"Gemini returned text (first 300 chars): {text[:300]}")
                    
                    # Check if text contains a URL
                    url_pattern = r'https?://[^\s]+\.(jpg|jpeg|png|gif|webp)'
                    url_match = re.search(url_pattern, text, re.IGNORECASE)
                    if url_match:
                        import requests
                        img_url = url_match.group(0)
                        logger.debug(f"Found image URL: {img_url}")
                        img_response = requests.get(img_url, timeout=30)
                        img_response.raise_for_status()
                        image_data = img_response.content
                        logger.debug("Downloaded image from URL")
                        break
                    
                    # Try to extract base64
                    base64_pattern = r'([A-Za-z0-9+/]{100,}={0,2})'
                    matches = re.findall(base64_pattern, text)
                    for match in matches:
                        try:
                            decoded = base64.b64decode(match)
                            if len(decoded) > 1000:
                                image_data = decoded
                                logger.debug("Found base64 encoded image")
                                break
                        except:
                            continue
                    
                    if image_data:
                        break
                    
                    # Check for data URL
                    data_url_pattern = r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)'
                    match = re.search(data_url_pattern, text)
                    if match:
                        try:
                            image_data = base64.b64decode(match.group(1))
                            logger.debug("Found image in data URL")
                            break
                        except:
                            pass
            
            if not image_data:
                error_text = response.text if hasattr(response, 'text') else "No image generated"
                logger.error(f"No image data found. Response: {error_text[:200]}")
                raise RuntimeError(f"Gemini 3.1 Flash Image returned no image. The model may not be available. Response: {error_text[:100]}")
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Gemini 3.1 Flash Image API call completed in {elapsed:.2f}ms")
            
            return image_data
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise RuntimeError(f"AI service error: {str(e)}")
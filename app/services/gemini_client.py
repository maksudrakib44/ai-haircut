import google.generativeai as genai
from PIL import Image
import io
import time
import base64
import asyncio
from loguru import logger
from config.settings import settings

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        logger.info(f"Gemini client initialized with model: {settings.gemini_model}")
        # Limit concurrent calls to 2 to avoid API rate limiting
        self._semaphore = asyncio.Semaphore(2)

    async def generate_hairstyle(self, image_bytes: bytes, style: str) -> bytes:
        """Generate a single hairstyle with concurrency control."""
        async with self._semaphore:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self._sync_generate_hairstyle,
                image_bytes,
                style
            )
    
    def _sync_generate_hairstyle(self, image_bytes: bytes, style: str) -> bytes:
        """Synchronous version that runs in a thread pool."""
        start_time = time.time()
        try:
            image = Image.open(io.BytesIO(image_bytes))
            prompt = settings.hairstyle_prompt_template.format(style=style)
            
            response = self.model.generate_content([prompt, image])
            
            if not response.candidates:
                raise RuntimeError("No candidates returned")
            
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                raise RuntimeError("No content parts")
            
            for part in candidate.content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    elapsed = (time.time() - start_time) * 1000
                    logger.debug(f"Generated '{style}' in {elapsed:.0f}ms")
                    return part.inline_data.data
            
            raise RuntimeError("No image data in response")
        except Exception as e:
            logger.error(f"Generation failed for '{style}': {str(e)}")
            raise RuntimeError(f"Failed to generate '{style}': {str(e)}")
    
    async def generate_multiple_hairstyles(
        self, 
        image_bytes: bytes, 
        styles: list
    ) -> list:
        """Generate multiple hairstyles concurrently."""
        tasks = []
        for style_item in styles:
            if isinstance(style_item, dict):
                style_desc = style_item.get('description', style_item.get('key', ''))
            else:
                style_desc = style_item
            tasks.append(self.generate_hairstyle(image_bytes, style_desc))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        output = []
        for i, result in enumerate(results):
            style_item = styles[i]
            if isinstance(style_item, dict):
                style_key = style_item.get('key', 'unknown')
                style_desc = style_item.get('description', style_key)
            else:
                style_key = style_item
                style_desc = style_item
            
            if isinstance(result, Exception):
                logger.error(f"Failed for {style_key}: {result}")
                continue
            
            image_base64 = base64.b64encode(result).decode('utf-8')
            output.append({
                'style_key': style_key,
                'style_description': style_desc,
                'image_base64': image_base64,
                'mime_type': 'image/jpeg'
            })
        
        return output
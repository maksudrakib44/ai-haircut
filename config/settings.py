import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        # Google Gemini API
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        # Use the image generation model (experimental, supports image output)
        self.gemini_model = "gemini-2.0-flash-exp-image-generation"
        
        # Server
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.reload = os.getenv("RELOAD", "false").lower() == "true"
        self.workers = int(os.getenv("WORKERS", "4"))
        
        # Image validation
        self.max_image_size_mb = int(os.getenv("MAX_IMAGE_SIZE_MB", "5"))
        allowed_ext_str = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png")
        self.allowed_extensions = [ext.strip() for ext in allowed_ext_str.split(",")]
        self.max_image_dimension = int(os.getenv("MAX_IMAGE_DIMENSION", "2048"))
        
        # Rate limiting
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
        self.rate_limit_per_hour = int(os.getenv("RATE_LIMIT_PER_HOUR", "100"))
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "json")
        
        # AI prompt template
        self.hairstyle_prompt_template = (
            "Transform the person's hairstyle to {style}. "
            "Keep the face, facial features, skin tone, and background exactly the same. "
            "Do not change the person's identity. Output a high-quality, realistic photo."
        )

settings = Settings()
import logging
import sys
from loguru import logger
from config.settings import settings

class InterceptHandler(logging.Handler):
    """Intercept standard logging messages and redirect them to Loguru."""
    
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging() -> None:
    """Configure logging for the application."""
    # Remove default handler
    logger.remove()
    
    # Add console handler with appropriate format
    if settings.log_format == "json":
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name} | {message}",
            level=settings.log_level,
            serialize=False
        )
    else:
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
            level=settings.log_level,
            colorize=True
        )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Set specific loggers to appropriate levels
    for log_name in ["uvicorn", "uvicorn.error", "fastapi"]:
        logging.getLogger(log_name).handlers = [InterceptHandler()]
        logging.getLogger(log_name).propagate = False
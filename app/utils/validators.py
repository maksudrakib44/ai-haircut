import imghdr
from fastapi import UploadFile, HTTPException
from config.settings import settings

async def validate_image(file: UploadFile) -> bytes:
    """
    Validate uploaded image file.
    Returns image bytes if valid, raises HTTPException otherwise.
    """
    # Check file size
    file.file.seek(0, 2)
    size_mb = file.file.tell() / (1024 * 1024)
    file.file.seek(0)
    
    if size_mb > settings.max_image_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"Image too large. Maximum allowed size: {settings.max_image_size_mb}MB"
        )
    
    # Check file extension
    filename = file.filename.lower()
    ext = filename.split('.')[-1] if '.' in filename else ''
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension. Allowed: {', '.join(settings.allowed_extensions)}"
        )
    
    # Read file content
    contents = await file.read()
    
    # Verify actual image type
    image_type = imghdr.what(None, contents)
    if image_type not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="File is not a valid image"
        )
    
    return contents
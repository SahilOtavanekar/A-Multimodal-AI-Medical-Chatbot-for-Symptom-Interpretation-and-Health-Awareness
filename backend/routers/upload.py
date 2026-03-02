from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from models import StandardResponse
from dependencies import verify_session, supabase
from limiter import limiter
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["Image Uploads"])

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

@router.post("/", response_model=StandardResponse)
@limiter.limit("2/minute")
async def upload_medical_image(request_data: Request, file: UploadFile = File(...), user=Depends(verify_session)):
    """
    Secure endpoint for uploading medical images or symptom pictures to Supabase Storage.
    Validates file extension and size.
    """
    try:
        # 1. Validate Extension
        ext = file.filename.split(".")[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File must be an image ({', '.join(ALLOWED_EXTENSIONS)})")
        
        # 2. Validate content size (Requires reading the spool)
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
             raise HTTPException(status_code=400, detail="Image exceeds default 5MB limit.")

        # 3. Create unique path in storage: user_id/uuid.ext
        file_path = f"{user.id}/{uuid.uuid4()}.{ext}"

        # 4. Upload to Supabase bucket
        response = supabase.storage.from_("medical_images").upload(
            path=file_path,
            file=content,
            file_options={"content-type": file.content_type}
        )
        
        # 5. Get Signed/Public URL for the frontend / AI to use later
        url_response = supabase.storage.from_("medical_images").get_public_url(file_path)

        return StandardResponse(
            success=True, 
            message="Image uploaded securely.",
            data={"url": url_response}
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Image upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload image securely.")

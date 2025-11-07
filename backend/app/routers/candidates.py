from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import logging

from app.database import get_db
from app.models import Candidate, User
from app.services.cloudinary_service import CloudinaryService

logger = logging.getLogger(__name__)
router = APIRouter()

# Schemas
class CandidateProfile(BaseModel):
    name: str
    email: str
    skills: list = []

class ResumeUploadResponse(BaseModel):
    status: str
    url: str
    public_id: str
    size: int
    format: str

# Endpoints
@router.get("/profile")
async def get_profile(db: Session = Depends(get_db)):
    """Get candidate profile"""
    # TODO: Add auth check
    return {"message": "Profile endpoint - Week 2"}

@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload resume to Cloudinary
    
    Supported formats: PDF, DOC, DOCX, TXT, images
    """
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "image/jpeg",
            "image/png"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: PDF, DOC, DOCX, TXT, JPG, PNG"
            )
        
        # TODO: Get user_id from auth token
        user_id = "test_user"
        
        # Upload to Cloudinary
        result = CloudinaryService.upload_resume(file, user_id)
        
        logger.info(f"✅ Resume uploaded: {result['url']}")
        
        return ResumeUploadResponse(
            status="success",
            url=result['url'],
            public_id=result['public_id'],
            size=result['size'],
            format=result['format']
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

@router.get("/recommendations")
async def get_recommendations(db: Session = Depends(get_db)):
    """Get job recommendations"""
    # TODO: Implement matching logic
    return {"message": "Recommendations - Week 2"}

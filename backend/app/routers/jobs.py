from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import uuid

from app.database import get_db
from app.models import Job, User

router = APIRouter()

# Schemas
class JobCreate(BaseModel):
    title: str
    jd_text: str
    required_skills: List[str] = []
    location: str
    salary_min: int = None
    salary_max: int = None
    remote: bool = False

class JobResponse(BaseModel):
    id: str
    title: str
    location: str
    status: str
    created_at: str

    class Config:
        from_attributes = True

# Endpoints
@router.post("/", response_model=dict)
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Create a new job posting"""
    # TODO: Add auth check for recruiter
    
    new_job = Job(
        company_id=uuid.uuid4(),  # TODO: Get from auth
        title=job.title,
        jd_text=job.jd_text,
        required_skills=job.required_skills,
        location=job.location,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        remote=job.remote
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {"id": str(new_job.id), "title": new_job.title, "status": "created"}

@router.get("/")
async def list_jobs(db: Session = Depends(get_db)):
    """List all jobs"""
    jobs = db.query(Job).filter(Job.status == "open").all()
    return {"jobs": [{"id": str(j.id), "title": j.title} for j in jobs]}

@router.get("/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get job details"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"id": str(job.id), "title": job.title}

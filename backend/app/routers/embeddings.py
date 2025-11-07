from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FAISSService

# Initialize FAISS on startup
FAISSService.initialize()

logger = logging.getLogger(__name__)
router = APIRouter()

# Schemas
class EmbeddingRequest(BaseModel):
    text: str

class SearchRequest(BaseModel):
    query_text: str
    n_results: int = 10

class AddResumeRequest(BaseModel):
    resume_id: str
    resume_text: str
    metadata: dict = None

# Endpoints
@router.post("/generate-embedding")
async def generate_embedding(request: EmbeddingRequest):
    """Generate embedding for text"""
    try:
        embedding = EmbeddingService.generate_embedding(request.text)
        if not embedding:
            raise HTTPException(status_code=400, detail="Failed to generate embedding")
        
        return {
            "status": "success",
            "embedding_dimension": len(embedding),
            "embedding": embedding[:10]  # Return first 10 for preview
        }
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/search-resumes")
async def search_resumes(request: SearchRequest):
    """Search for similar resumes"""
    try:
        # Generate embedding for query
        query_embedding = EmbeddingService.generate_embedding(request.query_text)
        if not query_embedding:
            raise HTTPException(status_code=400, detail="Failed to generate query embedding")
        
        # Search in FAISS
        results = FAISSService.search_resumes(query_embedding, request.n_results)
        if not results:
            raise HTTPException(status_code=400, detail="Search failed")
        
        return {
            "status": "success",
            "query": request.query_text,
            "results_count": len(results['ids']),
            "results": {
                "ids": results['ids'],
                "documents": results['documents'],
                "distances": results['distances']
            }
        }
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/add-resume")
async def add_resume(request: AddResumeRequest):
    """Add resume to FAISS"""
    try:
        # Generate embedding
        embedding = EmbeddingService.generate_embedding(request.resume_text)
        if not embedding:
            raise HTTPException(status_code=400, detail="Failed to generate embedding")
        
        # Add to FAISS
        success = FAISSService.add_resume(
            request.resume_id,
            request.resume_text,
            embedding,
            request.metadata
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add resume")
        
        return {
            "status": "success",
            "resume_id": request.resume_id,
            "message": "Resume added successfully"
        }
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/collection-stats")
async def get_stats():
    """Get collection statistics"""
    try:
        stats = FAISSService.get_collection_stats()
        return {"status": "success", "stats": stats}
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/model-info")
async def get_model_info():
    """Get embedding model information"""
    try:
        info = EmbeddingService.get_model_info()
        return {"status": "success", "model_info": info}
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Load embedding model (384-dimensional)
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("✅ Embedding model loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load embedding model: {str(e)}")
    model = None

class EmbeddingService:
    """Service for generating embeddings"""

    @staticmethod
    def generate_embedding(text: str):
        """Generate embedding for text"""
        try:
            if model is None:
                raise Exception("Embedding model not loaded")
            
            embedding = model.encode(text, convert_to_tensor=False)
            logger.info(f"✅ Embedding generated: {len(embedding)} dimensions")
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {str(e)}")
            return None

    @staticmethod
    def generate_embeddings_batch(texts: list):
        """Generate embeddings for multiple texts"""
        try:
            if model is None:
                raise Exception("Embedding model not loaded")
            
            embeddings = model.encode(texts, convert_to_tensor=False)
            logger.info(f"✅ Batch embeddings generated: {len(embeddings)} items")
            return [e.tolist() for e in embeddings]
        except Exception as e:
            logger.error(f"❌ Failed to generate batch embeddings: {str(e)}")
            return None

    @staticmethod
    def get_model_info():
        """Get model information"""
        return {
            "model_name": "all-MiniLM-L6-v2",
            "embedding_dimension": 384,
            "model_size": "small",
            "description": "Fast and efficient embedding model"
        }

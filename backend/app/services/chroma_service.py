import chromadb
from chromadb.config import Settings as ChromaSettings
import logging
import os

logger = logging.getLogger(__name__)

# Configure Chroma
chroma_settings = ChromaSettings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_data",
    anonymized_telemetry=False,
)

# Create persistent client
client = chromadb.Client(chroma_settings)

class ChromaService:
    """Service for handling vector embeddings with Chroma"""

    @staticmethod
    def get_or_create_collection(collection_name: str = "resumes"):
        """Get or create a collection"""
        try:
            collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"✅ Collection '{collection_name}' ready")
            return collection
        except Exception as e:
            logger.error(f"�� Failed to get/create collection: {str(e)}")
            raise

    @staticmethod
    def add_resume(
        resume_id: str,
        resume_text: str,
        embedding: list,
        metadata: dict = None
    ):
        """Add resume to Chroma"""
        try:
            collection = ChromaService.get_or_create_collection()
            
            if metadata is None:
                metadata = {}
            
            collection.add(
                ids=[resume_id],
                documents=[resume_text],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            
            logger.info(f"✅ Resume added: {resume_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add resume: {str(e)}")
            return False

    @staticmethod
    def search_resumes(
        query_embedding: list,
        n_results: int = 10
    ):
        """Search for similar resumes"""
        try:
            collection = ChromaService.get_or_create_collection()
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            logger.info(f"✅ Search completed: {len(results['ids'][0])} results")
            return results
        except Exception as e:
            logger.error(f"❌ Search failed: {str(e)}")
            return None

    @staticmethod
    def delete_resume(resume_id: str):
        """Delete resume from Chroma"""
        try:
            collection = ChromaService.get_or_create_collection()
            collection.delete(ids=[resume_id])
            logger.info(f"✅ Resume deleted: {resume_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete resume: {str(e)}")
            return False

    @staticmethod
    def get_resume(resume_id: str):
        """Get resume from Chroma"""
        try:
            collection = ChromaService.get_or_create_collection()
            result = collection.get(ids=[resume_id])
            
            if result and result['ids']:
                return {
                    "id": result['ids'][0],
                    "document": result['documents'][0],
                    "embedding": result['embeddings'][0],
                    "metadata": result['metadatas'][0]
                }
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get resume: {str(e)}")
            return None

    @staticmethod
    def get_collection_stats():
        """Get collection statistics"""
        try:
            collection = ChromaService.get_or_create_collection()
            count = collection.count()
            logger.info(f"✅ Collection stats: {count} items")
            return {"total_items": count}
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {str(e)}")
            return None

    @staticmethod
    def clear_collection():
        """Clear all data from collection"""
        try:
            collection = ChromaService.get_or_create_collection()
            # Get all IDs and delete them
            all_items = collection.get()
            if all_items['ids']:
                collection.delete(ids=all_items['ids'])
            logger.info("✅ Collection cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to clear collection: {str(e)}")
            return False

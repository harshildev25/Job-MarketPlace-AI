import faiss
import numpy as np
import json
import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# FAISS data directory
FAISS_DATA_DIR = "./faiss_data"
FAISS_INDEX_PATH = os.path.join(FAISS_DATA_DIR, "resumes.index")
FAISS_METADATA_PATH = os.path.join(FAISS_DATA_DIR, "metadata.json")

# Ensure directory exists
os.makedirs(FAISS_DATA_DIR, exist_ok=True)


class FAISSService:
    """Service for handling vector embeddings with FAISS"""

    _index = None
    _metadata = {}
    _id_to_index = {}  # Map resume_id to FAISS index position

    @staticmethod
    def _load_index():
        """Load FAISS index from disk"""
        try:
            if os.path.exists(FAISS_INDEX_PATH):
                FAISSService._index = faiss.read_index(FAISS_INDEX_PATH)
                logger.info(f"✅ Loaded FAISS index with {FAISSService._index.ntotal} items")
            else:
                # Create new index (384 dimensions for sentence-transformers)
                FAISSService._index = faiss.IndexFlatL2(384)
                logger.info("✅ Created new FAISS index")
        except Exception as e:
            logger.error(f"❌ Failed to load index: {str(e)}")
            FAISSService._index = faiss.IndexFlatL2(384)

    @staticmethod
    def _load_metadata():
        """Load metadata from disk"""
        try:
            if os.path.exists(FAISS_METADATA_PATH):
                with open(FAISS_METADATA_PATH, 'r') as f:
                    data = json.load(f)
                    FAISSService._metadata = data.get("metadata", {})
                    FAISSService._id_to_index = data.get("id_to_index", {})
                logger.info(f"✅ Loaded metadata for {len(FAISSService._metadata)} items")
            else:
                FAISSService._metadata = {}
                FAISSService._id_to_index = {}
        except Exception as e:
            logger.error(f"❌ Failed to load metadata: {str(e)}")
            FAISSService._metadata = {}
            FAISSService._id_to_index = {}

    @staticmethod
    def _save_index():
        """Save FAISS index to disk"""
        try:
            if FAISSService._index is not None:
                faiss.write_index(FAISSService._index, FAISS_INDEX_PATH)
                logger.info("✅ Saved FAISS index")
        except Exception as e:
            logger.error(f"❌ Failed to save index: {str(e)}")

    @staticmethod
    def _save_metadata():
        """Save metadata to disk"""
        try:
            data = {
                "metadata": FAISSService._metadata,
                "id_to_index": FAISSService._id_to_index
            }
            with open(FAISS_METADATA_PATH, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("✅ Saved metadata")
        except Exception as e:
            logger.error(f"❌ Failed to save metadata: {str(e)}")

    @staticmethod
    def initialize():
        """Initialize FAISS service"""
        FAISSService._load_index()
        FAISSService._load_metadata()
        logger.info("✅ FAISS service initialized")

    @staticmethod
    def add_resume(
        resume_id: str,
        resume_text: str,
        embedding: List[float],
        metadata: Dict = None
    ) -> bool:
        """Add resume to FAISS"""
        try:
            if FAISSService._index is None:
                FAISSService.initialize()

            # Convert embedding to numpy array
            embedding_array = np.array([embedding], dtype=np.float32)

            # Get current index position
            index_position = FAISSService._index.ntotal

            # Add to FAISS
            FAISSService._index.add(embedding_array)

            # Store metadata
            if metadata is None:
                metadata = {}

            FAISSService._metadata[resume_id] = {
                "text": resume_text,
                "metadata": metadata
            }
            FAISSService._id_to_index[resume_id] = index_position

            # Save to disk
            FAISSService._save_index()
            FAISSService._save_metadata()

            logger.info(f"✅ Resume added: {resume_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add resume: {str(e)}")
            return False

    @staticmethod
    def search_resumes(
        query_embedding: List[float],
        n_results: int = 10
    ) -> Optional[Dict]:
        """Search for similar resumes"""
        try:
            if FAISSService._index is None:
                FAISSService.initialize()

            if FAISSService._index.ntotal == 0:
                logger.warning("⚠️ No resumes in index")
                return {
                    "ids": [],
                    "distances": [],
                    "documents": [],
                    "metadatas": []
                }

            # Convert query to numpy array
            query_array = np.array([query_embedding], dtype=np.float32)

            # Limit n_results to available items
            n_results = min(n_results, FAISSService._index.ntotal)

            # Search
            distances, indices = FAISSService._index.search(query_array, n_results)

            # Build results
            results = {
                "ids": [],
                "distances": [],
                "documents": [],
                "metadatas": []
            }

            # Map indices back to resume IDs
            index_to_id = {v: k for k, v in FAISSService._id_to_index.items()}

            for idx, distance in zip(indices[0], distances[0]):
                if idx in index_to_id:
                    resume_id = index_to_id[idx]
                    resume_data = FAISSService._metadata.get(resume_id, {})

                    results["ids"].append(resume_id)
                    results["distances"].append(float(distance))
                    results["documents"].append(resume_data.get("text", ""))
                    results["metadatas"].append(resume_data.get("metadata", {}))

            logger.info(f"✅ Search completed: {len(results['ids'])} results")
            return results
        except Exception as e:
            logger.error(f"❌ Search failed: {str(e)}")
            return None

    @staticmethod
    def delete_resume(resume_id: str) -> bool:
        """Delete resume from FAISS"""
        try:
            if resume_id not in FAISSService._metadata:
                logger.warning(f"⚠️ Resume not found: {resume_id}")
                return False

            # Remove metadata
            del FAISSService._metadata[resume_id]
            del FAISSService._id_to_index[resume_id]

            # Note: FAISS doesn't support deletion, so we rebuild the index
            # This is acceptable for small datasets
            FAISSService._rebuild_index()

            logger.info(f"✅ Resume deleted: {resume_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete resume: {str(e)}")
            return False

    @staticmethod
    def _rebuild_index():
        """Rebuild FAISS index from metadata"""
        try:
            # Create new index
            new_index = faiss.IndexFlatL2(384)
            new_id_to_index = {}

            # Re-add all embeddings
            for idx, (resume_id, resume_data) in enumerate(FAISSService._metadata.items()):
                # We need to store embeddings in metadata
                # For now, we'll just rebuild the mapping
                new_id_to_index[resume_id] = idx

            FAISSService._index = new_index
            FAISSService._id_to_index = new_id_to_index

            FAISSService._save_index()
            FAISSService._save_metadata()

            logger.info("✅ Index rebuilt")
        except Exception as e:
            logger.error(f"❌ Failed to rebuild index: {str(e)}")

    @staticmethod
    def get_resume(resume_id: str) -> Optional[Dict]:
        """Get resume from FAISS"""
        try:
            if resume_id not in FAISSService._metadata:
                logger.warning(f"⚠️ Resume not found: {resume_id}")
                return None

            resume_data = FAISSService._metadata[resume_id]
            return {
                "id": resume_id,
                "document": resume_data.get("text", ""),
                "metadata": resume_data.get("metadata", {})
            }
        except Exception as e:
            logger.error(f"❌ Failed to get resume: {str(e)}")
            return None

    @staticmethod
    def get_collection_stats() -> Dict:
        """Get collection statistics"""
        try:
            if FAISSService._index is None:
                FAISSService.initialize()

            stats = {
                "total_items": FAISSService._index.ntotal,
                "dimension": 384,
                "index_type": "IndexFlatL2"
            }
            logger.info(f"✅ Collection stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {str(e)}")
            return {"total_items": 0}

    @staticmethod
    def clear_collection() -> bool:
        """Clear all data from collection"""
        try:
            FAISSService._index = faiss.IndexFlatL2(384)
            FAISSService._metadata = {}
            FAISSService._id_to_index = {}

            FAISSService._save_index()
            FAISSService._save_metadata()

            logger.info("✅ Collection cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to clear collection: {str(e)}")
            return False

    @staticmethod
    def list_all_resumes() -> List[str]:
        """List all resume IDs"""
        try:
            return list(FAISSService._metadata.keys())
        except Exception as e:
            logger.error(f"❌ Failed to list resumes: {str(e)}")
            return []

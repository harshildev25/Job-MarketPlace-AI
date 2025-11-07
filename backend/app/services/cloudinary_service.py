import cloudinary
import cloudinary.uploader
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

class CloudinaryService:
    """Service for handling file uploads to Cloudinary"""

    @staticmethod
    def upload_resume(file, user_id: str):
        """
        Upload resume to Cloudinary
        
        Args:
            file: File object from FastAPI
            user_id: User ID for organizing files
            
        Returns:
            dict: Upload result with URL and metadata
        """
        try:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file.file,
                folder=settings.CLOUDINARY_FOLDER,
                resource_type="auto",
                public_id=f"resume_{user_id}",
                overwrite=True,
                tags=["resume", user_id]
            )
            
            logger.info(f"✅ Resume uploaded: {result['public_id']}")
            
            return {
                "url": result['secure_url'],
                "public_id": result['public_id'],
                "size": result['bytes'],
                "format": result['format']
            }
        except Exception as e:
            logger.error(f"❌ Upload failed: {str(e)}")
            raise

    @staticmethod
    def upload_video(file, user_id: str):
        """
        Upload video to Cloudinary
        
        Args:
            file: File object from FastAPI
            user_id: User ID for organizing files
            
        Returns:
            dict: Upload result with URL and metadata
        """
        try:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file.file,
                folder=f"{settings.CLOUDINARY_FOLDER}/videos",
                resource_type="video",
                public_id=f"video_{user_id}",
                overwrite=True,
                tags=["video", user_id]
            )
            
            logger.info(f"✅ Video uploaded: {result['public_id']}")
            
            return {
                "url": result['secure_url'],
                "public_id": result['public_id'],
                "size": result['bytes'],
                "duration": result.get('duration', 0)
            }
        except Exception as e:
            logger.error(f"❌ Video upload failed: {str(e)}")
            raise

    @staticmethod
    def upload_image(file, user_id: str, image_type: str = "profile"):
        """
        Upload image to Cloudinary
        
        Args:
            file: File object from FastAPI
            user_id: User ID for organizing files
            image_type: Type of image (profile, cover, etc.)
            
        Returns:
            dict: Upload result with URL and metadata
        """
        try:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file.file,
                folder=f"{settings.CLOUDINARY_FOLDER}/images",
                resource_type="image",
                public_id=f"{image_type}_{user_id}",
                overwrite=True,
                tags=["image", image_type, user_id],
                transformation=[
                    {"width": 500, "height": 500, "crop": "fill"}
                ]
            )
            
            logger.info(f"✅ Image uploaded: {result['public_id']}")
            
            return {
                "url": result['secure_url'],
                "public_id": result['public_id'],
                "size": result['bytes'],
                "width": result['width'],
                "height": result['height']
            }
        except Exception as e:
            logger.error(f"❌ Image upload failed: {str(e)}")
            raise

    @staticmethod
    def delete_file(public_id: str, resource_type: str = "image"):
        """
        Delete file from Cloudinary
        
        Args:
            public_id: Public ID of the file
            resource_type: Type of resource (image, video, raw)
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            logger.info(f"✅ File deleted: {public_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Delete failed: {str(e)}")
            return False

    @staticmethod
    def get_file_url(public_id: str):
        """
        Get file URL from Cloudinary
        
        Args:
            public_id: Public ID of the file
            
        Returns:
            str: Secure URL of the file
        """
        try:
            url = cloudinary.CloudinaryResource(public_id).build_url(secure=True)
            return url
        except Exception as e:
            logger.error(f"❌ Get URL failed: {str(e)}")
            return None

    @staticmethod
    def transform_image(public_id: str, transformations: dict):
        """
        Get transformed image URL
        
        Args:
            public_id: Public ID of the image
            transformations: Transformation parameters
            
        Returns:
            str: URL of transformed image
        """
        try:
            url = cloudinary.CloudinaryResource(public_id).build_url(
                secure=True,
                **transformations
            )
            return url
        except Exception as e:
            logger.error(f"❌ Transform failed: {str(e)}")
            return None

    @staticmethod
    def get_usage_stats():
        """
        Get Cloudinary account usage statistics
        
        Returns:
            dict: Usage statistics
        """
        try:
            result = cloudinary.api.usage()
            return {
                "storage": result.get('storage', 0),
                "bandwidth": result.get('bandwidth', 0),
                "requests": result.get('requests', 0),
                "transformations": result.get('transformations', 0)
            }
        except Exception as e:
            logger.error(f"❌ Get usage failed: {str(e)}")
            return None

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "TalentIQ"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/dbname"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # FAISS (Vector Database)
    FAISS_PERSIST_DIR: str = "./faiss_data"
    FAISS_COLLECTION_NAME: str = "resumes"

    # Cloudinary (replaces MinIO)
    CLOUDINARY_CLOUD_NAME: str = "your_cloud_name"
    CLOUDINARY_API_KEY: str = "your_api_key"
    CLOUDINARY_API_SECRET: str = "your_api_secret"
    CLOUDINARY_FOLDER: str = "talentiq-resumes"

    # JWT
    JWT_SECRET: str = "your_super_secret_jwt_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

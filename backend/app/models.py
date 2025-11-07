from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="candidate")  # admin, recruiter, candidate
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="users")
    candidate = relationship("Candidate", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.email}>"


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    verified = Column(Boolean, default=False)
    plan = Column(String(50), default="free")  # free, pro, enterprise
    billing_email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company")

    def __repr__(self):
        return f"<Company {self.name}>"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False)
    jd_text = Column(Text)
    required_skills = Column(JSON, default=[])  # ["Python", "Django"]
    location = Column(String(255))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    remote = Column(Boolean, default=False)
    status = Column(String(50), default="open")  # open, closed, draft
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job")

    def __repr__(self):
        return f"<Job {self.title}>"


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    parsed_profile = Column(JSON, default={})  # structured resume data
    resume_url = Column(String(255))
    profile_completion = Column(Integer, default=0)  # 0-100%
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="candidate")
    applications = relationship("Application", back_populates="candidate")

    def __repr__(self):
        return f"<Candidate {self.user.email}>"


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    source = Column(String(50), default="upload")  # upload, email, passive, referral
    fit_score = Column(Numeric(3, 2), default=0.0)
    rank = Column(Integer)
    status = Column(String(50), default="applied")  # applied, reviewed, interview, offer, hired, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")

    def __repr__(self):
        return f"<Application {self.candidate_id} -> {self.job_id}>"

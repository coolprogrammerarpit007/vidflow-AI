import uuid
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base
import enum

# Define Enum for Job Statuses
class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    STITCHING = "STITCHING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    credit_balance = Column(Integer, default=10) # Give new users 10 credits

    # Relationships
    jobs = relationship("VideoJob", back_populates="owner")

class VideoJob(Base):
    __tablename__ = "video_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    prompt = Column(String(1000), nullable=False)
    requested_duration = Column(Integer, nullable=False) # In seconds
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    external_task_ids = Column(JSON, nullable=True) # Store array of Veo/Runway IDs
    s3_url = Column(String(500), nullable=True)

    # Relationships
    owner = relationship("User", back_populates="jobs")
    chunks = relationship("VideoChunk", back_populates="job", cascade="all, delete-orphan")

class VideoChunk(Base):
    __tablename__ = "video_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("video_jobs.id"))
    chunk_index = Column(Integer, nullable=False) # e.g., 1, 2, 3 for ordering
    s3_path = Column(String(500), nullable=True)

    # Relationships
    job = relationship("VideoJob", back_populates="chunks")
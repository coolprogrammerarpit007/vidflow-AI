from pydantic import BaseModel, Field
from typing import Optional, List
from .models import JobStatus

# --- Requests (Data coming IN from the Frontend) ---

class VideoRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=1000, description="The video description")
    duration: int = Field(..., ge=5, le=60, description="Duration in seconds (5 to 60)")
    # We can add aspect_ratio later if needed

# --- Responses (Data going OUT to the Frontend) ---

class VideoJobResponse(BaseModel):
    id: str
    prompt: str
    requested_duration: int
    status: JobStatus
    s3_url: Optional[str] = None

    class Config:
        from_attributes = True # Tells Pydantic to read SQLAlchemy models
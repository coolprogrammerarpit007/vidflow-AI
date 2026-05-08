from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import database, models, schemas
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VidFlow AI Video Engine")

@app.get("/")
async def root():
    return {"message": "VidFlow AI Engine is Online"}

@app.post("/generate", response_model=schemas.VideoJobResponse)
async def create_video_request(request: schemas.VideoRequest, db: Session = Depends(database.get_db)):
    # 1. Logic to check credits
    # 2. Logic to create DB entry
    # 3. Logic to trigger Celery worker
    return {"job_id": "placeholder-id", "status": "pending"}
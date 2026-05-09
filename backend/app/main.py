import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import engine, get_db
from . import models, schemas
from .worker import generate_video_task

# 1. Create a local directory to hold our generated videos if it doesn't exist
os.makedirs("static/videos", exist_ok=True)

# 2. Tell SQLAlchemy to create the tables in MySQL
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VidFlow AI Video Engine")

# 3. Mount the static directory so videos can be accessed via URL in the browser
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "VidFlow AI Engine is Online"}

@app.post("/setup-test-user")
def setup_test_user(db: Session = Depends(get_db)):
    """Seed a test user with 100 credits so we can test the API."""
    user = db.query(models.User).filter(models.User.email == "arpit@example.com").first()
    if not user:
        user = models.User(email="arpit@example.com", credit_balance=100)
        db.add(user)
        db.commit()
        db.refresh(user)
    return {"message": "Test user ready", "user_id": user.id, "credits": user.credit_balance}

@app.post("/generate", response_model=schemas.VideoJobResponse)
async def create_video_request(request: schemas.VideoRequest, db: Session = Depends(get_db)):
    """The main endpoint to request a new AI video generation."""
    
    # 1. Get our test user
    user = db.query(models.User).filter(models.User.email == "arpit@example.com").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Run /setup-test-user first.")

    # 2. Credit Check (1 credit per second of video)
    if user.credit_balance < request.duration:
        raise HTTPException(status_code=400, detail="Insufficient credits.")

    # 3. Create the Job Record in MySQL
    new_job = models.VideoJob(
        user_id=user.id,
        prompt=request.prompt,
        requested_duration=request.duration,
        status=models.JobStatus.PENDING
    )
    
    # 4. Deduct credits and save
    user.credit_balance -= request.duration
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # 5. Send the job to the Celery/Redis queue to be processed in the background
    generate_video_task.delay(new_job.id) 
    
    return new_job
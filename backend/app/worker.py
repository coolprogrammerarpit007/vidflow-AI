import time
import os
from celery import Celery
from .config import settings
from .utils import stitch_videos

# Initialize Celery connected to local Redis
celery_app = Celery(
    "vidflow_worker", 
    broker=settings.REDIS_URL, 
    backend=settings.REDIS_URL
)

@celery_app.task(name="generate_video_task")
def generate_video_task(job_id: str):
    """The background task that handles video generation, chunking, and stitching."""
    from .database import SessionLocal
    from .models import VideoJob, JobStatus

    db = SessionLocal()
    job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
    
    if not job:
        return "Job not found"

    try:
        # 1. Start Processing Phase
        job.status = JobStatus.PROCESSING
        db.commit()
        print(f"\n--- Started Job: {job_id} ---")

        # 2. Calculate Chunks (Assuming API limit is 5 seconds per generation)
        chunk_length = 5
        total_chunks = max(1, job.requested_duration // chunk_length) 
        
        generated_chunk_paths = []

        # 3. Generating Phase (Currently simulated)
        for i in range(total_chunks):
            print(f"Generating chunk {i+1} of {total_chunks}...")
            time.sleep(3) # Simulating API network wait time
            
            # Using our local dummy file to simulate a returned video
            dummy_chunk_path = "static/videos/sample.mp4" 
            generated_chunk_paths.append(dummy_chunk_path)

        # 4. Stitching Phase (If the video is longer than 5 seconds)
        if len(generated_chunk_paths) > 1:
            job.status = JobStatus.STITCHING
            db.commit()
            print("Stitching chunks together using FFmpeg...")
            
            final_filename = f"{job_id}_final.mp4"
            final_path = f"static/videos/{final_filename}"
            
            # Call our FFmpeg utility function
            stitch_videos(generated_chunk_paths, final_path)
        else:
            # If it's just 5 seconds, no stitching is needed
            final_filename = "sample.mp4" 

        # 5. Completion Phase
        job.status = JobStatus.COMPLETED
        # Save the local FastAPI URL so the frontend can display it
        job.s3_url = f"http://127.0.0.1:8000/static/videos/{final_filename}"
        db.commit()
        
        print(f"--- Finished Job: {job_id} ---\n")
        return "Success"

    except Exception as e:
        db.rollback()
        # Mark as failed in DB if anything goes wrong (like an FFmpeg error)
        job.status = JobStatus.FAILED
        db.commit()
        print(f"Error processing job {job_id}: {str(e)}")
        return "Failed"
    finally:
        db.close()
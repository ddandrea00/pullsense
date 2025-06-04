import sys
import os

# Add the current directory to Python path so Celery can find our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from celery import Celery
from config import settings

# Create Celery application
app = Celery('pullsense', broker=settings.REDIS_URL)

# Basic configuration
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

@app.task
def analyze_pr_task(pr_id: int):
    """
    Background task to analyze a pull request.
    This runs in a separate process!
    """
    print(f"🔄 Starting analysis for PR ID: {pr_id}")
    
    import time
    start_time = time.time()
    
    # Import here to avoid circular imports
    from database import SessionLocal, PullRequest, CodeReview
    from services.ai_analyzer import analyzer
    
    db = SessionLocal()
    try:
        # Get PR from database
        pr = db.query(PullRequest).filter_by(id=pr_id).first()
        if not pr:
            print(f"❌ PR with ID {pr_id} not found")
            return {"error": "PR not found"}
        
        print(f"📝 Analyzing PR #{pr.pr_number}: {pr.title}")
        
        # Perform AI analysis
        result = analyzer.analyze_pr({
            "title": pr.title,
            "body": pr.raw_data.get("pull_request", {}).get("body", ""),
            "author": pr.author
        })
        
        # Calculate time taken
        analysis_time = time.time() - start_time
        
        # Save to database
        review = CodeReview(
            pull_request_id=pr.id,
            analysis_text=result.get("analysis", "No analysis generated"),
            analysis_status=result.get("status", "error"),
            model_used=result.get("model", "unknown"),
            analysis_time_seconds=round(analysis_time, 2)
        )
        
        db.add(review)
        db.commit()
        db.refresh(review)
        
        print(f"💾 Saved analysis to database with ID: {review.id}")
        print(f"✅ Analysis complete for PR {pr_id} in {analysis_time:.2f} seconds")
        
        return {
            "status": "success",
            "review_id": review.id,
            "pr_id": pr_id,
            "time_taken": analysis_time
        }
        
    except Exception as e:
        print(f"❌ Error analyzing PR {pr_id}: {e}")
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

@app.task
def test_task(message: str = "Hello"):
    """Simple test task to verify Celery is working"""
    import time
    print(f"🎯 Test task received: {message}")
    time.sleep(2)  # Simulate some work
    print("✅ Test task completed")
    return {"status": "success", "message": f"Processed: {message}"}
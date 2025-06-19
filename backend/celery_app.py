import sys
import os

# Add the current directory to Python path so Celery can find our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from celery import Celery
from config import settings
import asyncio
import json

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

def broadcast_analysis_complete(pr_id: int, status: str):
    """Broadcast analysis completion to WebSocket clients."""
    try:
        # Import here to avoid circular imports
        import redis
        from config import settings
        
        # Use Redis to publish the message
        r = redis.from_url(settings.REDIS_URL)
        message = {
            "type": "analysis_complete",
            "data": {
                "pr_id": pr_id,
                "status": status
            }
        }
        r.publish("websocket_updates", json.dumps(message))
    except Exception as e:
        print(f"❌ Failed to broadcast update: {e}")

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
    from services.github_service import github_service
    
    db = SessionLocal()
    try:
        # Get PR from database
        pr = db.query(PullRequest).filter_by(id=pr_id).first()
        if not pr:
            print(f"❌ PR with ID {pr_id} not found")
            return {"error": "PR not found"}
        
        print(f"📝 Analyzing PR #{pr.pr_number}: {pr.title}")
        
        # Try to get real diff from GitHub
        diff_data = None
        if pr.repo_name and pr.pr_number:
            print(f"🔍 Fetching diff from GitHub for {pr.repo_name} PR #{pr.pr_number}")
            diff_data = github_service.get_pr_diff(pr.repo_name, pr.pr_number)
            if diff_data:
                print(f"✅ Got diff: {diff_data['changed_files']} files changed")
                print(f"📊 +{diff_data['additions']} -{diff_data['deletions']} lines")
            else:
                print("⚠️  Could not fetch diff from GitHub")
        
        # Perform AI analysis with diff data
        result = analyzer.analyze_pr({
            "title": pr.title,
            "body": pr.raw_data.get("pull_request", {}).get("body", ""),
            "author": pr.author,
            "diff_data": diff_data  # Pass the GitHub diff data
        })
        
        # Calculate processing time
        analysis_time = time.time() - start_time
        
        # Save analysis results to database
        review = CodeReview(
            pull_request_id=pr.id,
            analysis_text=result.get("analysis", "No analysis generated"),
            analysis_status=result.get("status", "error"),
            model_used=result.get("model", "unknown"),
            analysis_time_seconds=round(analysis_time, 2)
        )
        
        db.add(review)
        db.commit()
        db.refresh(review)  # Get the generated ID
        
        print(f"💾 Saved analysis to database with ID: {review.id}")
        print(f"✅ Analysis complete for PR {pr_id} in {analysis_time:.2f} seconds")
        
        # Broadcast completion to WebSocket clients
        broadcast_analysis_complete(pr_id, "completed")
        
        return {
            "status": "success",
            "review_id": review.id,
            "pr_id": pr_id,
            "time_taken": analysis_time,
            "used_github_diff": diff_data is not None
        }
        
    except Exception as e:
        print(f"❌ Error analyzing PR {pr_id}: {e}")
        db.rollback()  # Undo any partial changes
        
        # Broadcast error status
        broadcast_analysis_complete(pr_id, "error")
        
        return {"status": "error", "error": str(e)}
    finally:
        db.close()  # Always cleanup database connection

@app.task
def test_task(message: str = "Hello"):
    """Simple test task to verify Celery is working"""
    import time
    print(f"🎯 Test task received: {message}")
    time.sleep(2)  # Simulate some work
    print("✅ Test task completed")
    return {"status": "success", "message": f"Processed: {message}"}
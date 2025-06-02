from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from datetime import datetime
from database import SessionLocal, PullRequest
import json
import os

app = FastAPI(title="PullSense API")

# In-memory storage for now (we'll add database later)
webhooks_received = []

@app.get("/")
def root():
    return {
        "app": "PullSense",
        "status": "running",
        "webhooks_received": len(webhooks_received)
    }

@app.post("/webhook/github")
async def github_webhook(request: Request):
    # Get event type from GitHub's headers
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    
    # Parse the JSON payload
    payload = await request.json()
    
    # Log what we received (helps with debugging)
    print(f"\n🎯 Received {event_type} event")
    
    # Only process pull_request events for now
    if event_type == "pull_request":
        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {})
        
        # Extract the data we need
        pr_data = {
            "repo_name": repo.get("full_name"),
            "pr_number": pr.get("number"),
            "title": pr.get("title"),
            "author": pr.get("user", {}).get("login"),
            "action": payload.get("action"),
            "raw_data": payload  # Store everything for later
        }
        
        # Print what we're saving (helpful for development)
        print(f"📝 PR #{pr_data['pr_number']}: {pr_data['title']}")
        print(f"👤 Author: {pr_data['author']}")
        print(f"🔄 Action: {pr_data['action']}")
        
        # Save to database
        db = SessionLocal()
        try:
            # Create new PullRequest object
            db_pr = PullRequest(**pr_data)
            # ** unpacks the dictionary into keyword arguments
            
            db.add(db_pr)  # Add to session
            db.commit()     # Save to database
            db.refresh(db_pr)  # Get the ID that was assigned
            
            print(f"💾 Saved to database with ID: {db_pr.id}")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            db.rollback()  # Undo changes if error
            
        finally:
            db.close()  # Always close the session
    
    # Still store in memory for comparison
    webhook_data = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "payload": payload
    }
    webhooks_received.append(webhook_data)
    
    return {"status": "received", "event": event_type}

@app.get("/webhooks")
def list_webhooks():
    return {
        "count": len(webhooks_received),
        "webhooks": webhooks_received[-10:]  # Last 10
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

@app.get("/pull-requests")
def get_pull_requests():
    """Get all saved pull requests from database"""
    db = SessionLocal()
    try:
        #Query all PRs, ordered by newest first
        prs = db.query(PullRequest)\
            .order_by(PullRequest.created_at.desc())\
            .limit(20)\
            .all()

       # Convert to JSON-friendly format
        return {
            "count": len(prs),
            "pull_requests": [
                {
                    "id": pr.id,
                    "repo": pr.repo_name,
                    "number": pr.pr_number,
                    "title": pr.title,
                    "author": pr.author,
                    "action": pr.action,
                    "created": pr.created_at.isoformat()
                }
                for pr in prs
            ]
        }
    finally:
        db.close()

@app.get("/stats")
def get_stats():
    """Get statistics about stored PRs"""
    db = SessionLocal()
    try:
        total_prs = db.query(PullRequest).count()
        
        # Count by action
        from sqlalchemy import func
        action_counts = db.query(
            PullRequest.action,
            func.count(PullRequest.id)
        ).group_by(PullRequest.action).all()
        
        # Count by repository
        repo_counts = db.query(
            PullRequest.repo_name,
            func.count(PullRequest.id)
        ).group_by(PullRequest.repo_name).all()
        
        return {
            "total_prs": total_prs,
            "by_action": dict(action_counts),
            "by_repository": dict(repo_counts),
            "database": "SQLite (development)"
        }
    finally:
        db.close()
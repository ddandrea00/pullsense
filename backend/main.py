from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware  
from celery_app import analyze_pr_task, test_task
from pydantic import BaseModel
from datetime import datetime
from database import SessionLocal, PullRequest
from database import CodeReview
from sqlalchemy.orm import joinedload
from config import settings  
from services.github_service import github_service
from typing import List


import json
import os
import asyncio


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"📡 WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"📡 WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

app = FastAPI(title="PullSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://localhost:5174",  # Vite alternate
        "http://127.0.0.1:5173",  # Alternative localhost
        "http://localhost:4173",  # Vite preview
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory storage for now (we'll add database later)
webhooks_received = []

@app.get("/")
def root():
    return {
        "app": "PullSense",
        "status": "running",
        "webhooks_received": len(webhooks_received)
    }

@app.get("/webhooks")
def list_webhooks():
    return {
        "count": len(webhooks_received),
        "webhooks": webhooks_received[-10:]  # Last 10
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


@app.post("/webhook/github")
async def github_webhook(request: Request):
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    payload = await request.json()
    
    print(f"\n🎯 Received {event_type} event")
    
    if event_type == "pull_request":
        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {})
        
        db = SessionLocal()
        try:
            db_pr = PullRequest(
                repo_name=repo.get("full_name"),
                pr_number=pr.get("number"),
                title=pr.get("title"),
                author=pr.get("user", {}).get("login"),
                action=payload.get("action"),
                raw_data=payload
            )
            db.add(db_pr)
            db.commit()
            db.refresh(db_pr)
            
            print(f"💾 Saved PR #{pr.get('number')} to database")
            
            if payload.get("action") in ["opened", "synchronize"]:
                print(f"🤖 Queuing AI analysis for PR {db_pr.id}")
                analyze_pr_task.delay(db_pr.id)
            
        finally:
            db.close()
    
    webhook_data = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "payload": payload
    }
    webhooks_received.append(webhook_data)
    
    if event_type == "pull_request" and payload.get("action") == "opened":
        await manager.broadcast({
            "type": "pr_created",
            "data": {
                "pr_id": db_pr.id,
                "pr_number": db_pr.pr_number,
                "title": db_pr.title,
                "status": "pending"
            }
    })
    
    return {"status": "received", "event": event_type}


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
        
@app.get("/pull-requests/{pr_id}/analysis")
def get_pr_analysis(pr_id: int):
    """Get the latest AI analysis for a pull request"""
    db = SessionLocal()
    try:
        # Get PR with its reviews
        pr = db.query(PullRequest).filter_by(id=pr_id).first()
        if not pr:
            raise HTTPException(status_code=404, detail="Pull request not found")
        
        # Get the latest review
        review = db.query(CodeReview)\
            .filter_by(pull_request_id=pr_id)\
            .order_by(CodeReview.created_at.desc())\
            .first()
        
        if not review:
            return {
                "status": "pending",
                "message": "No analysis found. Trigger analysis with POST /analyze/{pr_id}"
            }
        
        return {
            "pull_request": {
                "id": pr.id,
                "number": pr.pr_number,
                "title": pr.title,
                "author": pr.author,
                "action": pr.action
            },
            "analysis": {
                "id": review.id,
                "status": review.analysis_status,
                "text": review.analysis_text,
                "model": review.model_used,
                "created_at": review.created_at.isoformat(),
                "analysis_time": review.analysis_time_seconds
            }
        }
    finally:
        db.close()

@app.get("/stats")
def get_stats():
    """Get statistics about the system"""
    db = SessionLocal()
    try:
        total_prs = db.query(PullRequest).count()
        total_reviews = db.query(CodeReview).count()
        
        # Get review status breakdown
        from sqlalchemy import func
        status_counts = db.query(
            CodeReview.analysis_status,
            func.count(CodeReview.id)
        ).group_by(CodeReview.analysis_status).all()
        
        return {
            "total_prs": total_prs,
            "total_reviews": total_reviews,
            "reviews_by_status": dict(status_counts),
            "celery_status": "Check worker terminal",
            "ai_enabled": bool(settings.OPENAI_API_KEY)
        }
    finally:
        db.close()


@app.post("/test/celery")
def test_celery():
    """Test endpoint to verify Celery is working"""
    # .delay() sends the task to background queue
    task = test_task.delay("Testing Celery!")
    
    return {
        "message": "Test task queued",
        "task_id": task.id,
        "check_worker_terminal": "You should see output there!"
    }

@app.post("/analyze/{pr_id}")
def trigger_analysis(pr_id: int):
    """Manually trigger analysis for a specific PR"""
    # Check if PR exists
    db = SessionLocal()
    try:
        pr = db.query(PullRequest).filter_by(id=pr_id).first()
        if not pr:
            raise HTTPException(status_code=404, detail="PR not found")
        
        # Queue the analysis
        task = analyze_pr_task.delay(pr_id)
        
        return {
            "message": f"Analysis queued for PR #{pr.pr_number}",
            "pr_title": pr.title,
            "task_id": task.id
        }
    finally:
        db.close()
        
@app.get("/dashboard")
def get_dashboard():
    """Get overview of all PRs and their analysis status"""
    db = SessionLocal()
    try:
        # Get recent PRs
        prs = db.query(PullRequest)\
            .order_by(PullRequest.created_at.desc())\
            .limit(20)\
            .all()
        
        dashboard_data = []
        for pr in prs:
            # Check if PR has been analyzed
            review = db.query(CodeReview)\
                .filter_by(pull_request_id=pr.id)\
                .order_by(CodeReview.created_at.desc())\
                .first()
            
            dashboard_data.append({
                "pr_id": pr.id,
                "pr_number": pr.pr_number,
                "title": pr.title,
                "author": pr.author,
                "repo": pr.repo_name,
                "created_at": pr.created_at.isoformat(),
                "analysis_status": review.analysis_status if review else "not_analyzed",
                "analyzed_at": review.created_at.isoformat() if review else None
            })
        
        return {
            "total_prs": len(prs),
            "analyzed": sum(1 for item in dashboard_data if item["analysis_status"] != "not_analyzed"),
            "pull_requests": dashboard_data
        }
    finally:
        db.close()
        
        
@app.get("/github/rate-limit")
def get_github_rate_limit():
    """Check GitHub API rate limit status"""
    return github_service.get_rate_limit()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back or handle client messages
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
# SQLite for quick start (we'll migrate to PostgreSQL later)
engine = create_engine("sqlite:///./pullsense.db")
# Why SQLite? No setup needed - just a file. Perfect for development.
# The ./ means "current directory"

SessionLocal = sessionmaker(bind=engine)
# SessionLocal is a factory. Each time we call it, we get a new database session
# Think of a session like a "workspace" for database operations

Base = declarative_base()
# Base is the parent class for all our database models
# SQLAlchemy uses this to track all tables

class PullRequest(Base):
    __tablename__ = "pull_requests"
    
    id = Column(Integer, primary_key=True)
    # Every table needs a primary key - unique identifier for each row
    
    repo_name = Column(String)
    # Which repository this PR belongs to (e.g., "facebook/react")
    
    pr_number = Column(Integer)
    # GitHub's PR number (e.g., PR #123)
    
    title = Column(String)
    # The PR title - what the developer is trying to do
    
    author = Column(String)
    # GitHub username of who created the PR
    
    action = Column(String)
    # What happened: "opened", "closed", "reopened", "synchronize" (updated)
    
    raw_data = Column(JSON)
    # Store the entire webhook payload - useful for debugging and future features
    # JSON column type stores Python dicts as JSON in database
    
    created_at = Column(DateTime, default=datetime.utcnow)
    # When WE received this webhook (not when PR was created)
    # default= means SQLAlchemy automatically sets this

class CodeReview(Base):
    __tablename__ = "code_reviews"
    
    id = Column(Integer, primary_key=True)
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"))
    
    # Analysis results from AI
    analysis_text = Column(Text)  # The main analysis
    analysis_status = Column(String)  # 'completed', 'error', 'mock'
    model_used = Column(String)  # Which AI model was used
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    analysis_time_seconds = Column(Float)  # How long analysis took
    
    # Relationship back to PR
    pull_request = relationship("PullRequest", backref="reviews")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    
# Create the actual database tables
Base.metadata.create_all(bind=engine)
# This reads all classes that inherit from Base and creates their tables
# Safe to run multiple times - won't recreate existing tables
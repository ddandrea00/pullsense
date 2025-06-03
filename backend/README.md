# PullSense 🔍

AI-powered code review assistant that analyzes GitHub pull requests in real-time.

## Overview

PullSense uses webhooks to receive GitHub pull request events and provides intelligent code review suggestions using AI analysis.

## Tech Stack

- **Backend**: FastAPI + Python 3.11
- **Database**: SQLAlchemy + SQLite (PostgreSQL in production)
- **AI**: OpenAI GPT-4 (coming in v2)
- **Infrastructure**: Docker + Kubernetes (coming soon)

## Features

- [x] Real-time webhook processing
- [x] PR data persistence
- [x] RESTful API
- [ ] AI code analysis (in progress)
- [ ] Review suggestions
- [ ] Security scanning

## Local Development

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/pullsense.git
cd pullsense

# Setup Python environment
cd backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

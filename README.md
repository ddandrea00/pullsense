```markdown
# PullSense 🔍

AI-powered code review assistant that analyzes GitHub pull requests automatically using OpenAI.

## Overview

PullSense receives GitHub webhooks, queues them for asynchronous processing, analyzes PR content using AI, and provides intelligent code review feedback. Built with modern Python async architecture for scalability and reliability.

## Features

- ✅ Real-time webhook processing from GitHub
- ✅ Asynchronous AI analysis with OpenAI GPT
- ✅ Background job processing with Celery + Redis
- ✅ Persistent storage with SQLAlchemy ORM
- ✅ RESTful API with automatic documentation
- ✅ Graceful error handling with mock fallback
- ✅ Dashboard view of all PR analyses
- ✅ Performance tracking and metrics

## Architecture
```

GitHub Webhooks → FastAPI → Redis Queue → Celery Workers → OpenAI
↓ ↓
SQLite ←───────────────────────┘

````

## Tech Stack

- **Backend Framework**: FastAPI (Python 3.11+)
- **Task Queue**: Celery + Redis
- **Database**: SQLAlchemy + SQLite (PostgreSQL ready)
- **AI Integration**: OpenAI GPT-3.5/GPT-4
- **API Documentation**: OpenAPI/Swagger (automatic)

## Prerequisites

- Python 3.11+
- Redis server
- Git
- OpenAI API key (optional - uses mock analysis without it)

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/pullsense.git
cd pullsense
````

2. **Set up Python environment**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key (optional)
```

5. **Install Redis**

```bash
# macOS
brew install redis

# Ubuntu/Debian
sudo apt-get install redis-server

# Start Redis
redis-server
```

## Running the Application

You need three terminal windows:

### Terminal 1: Redis Server

```bash
redis-server
```

### Terminal 2: Celery Worker

```bash
cd backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info
```

### Terminal 3: FastAPI Server

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Interactive API documentation is available at http://localhost:8000/docs

### Key Endpoints

#### Webhook Processing

- `POST /webhook/github` - Receive GitHub PR webhooks

#### Analysis Management

- `POST /analyze/{pr_id}` - Manually trigger analysis for a PR
- `GET /pull-requests/{pr_id}/analysis` - Get analysis results

#### Dashboard & Monitoring

- `GET /pull-requests` - List all pull requests
- `GET /dashboard` - Overview with analysis status
- `GET /stats` - System statistics

#### Testing

- `POST /test/celery` - Verify Celery is working

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# OpenAI Configuration (optional - uses mock if not provided)
OPENAI_API_KEY=sk-your-api-key-here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Database Configuration
DATABASE_URL=sqlite:///./pullsense.db

# For production PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/pullsense
```

### GitHub Webhook Setup

1. Go to your GitHub repository settings
2. Navigate to Webhooks → Add webhook
3. Set Payload URL: `https://your-domain.com/webhook/github`
4. Content type: `application/json`
5. Select events: Pull requests
6. Save webhook

For local development, use ngrok to expose your local server:

```bash
ngrok http 8000
```

## Testing

### Run Test Suite

```bash
cd backend
python -m pytest tests/
```

### Test Individual Components

```bash
# Test webhook processing
python tests/test_webhooks.py

# Test full analysis flow
python tests/test_full_flow.py
```

### Manual Testing

```bash
# Test Celery connectivity
curl -X POST http://localhost:8000/test/celery

# Trigger analysis for PR ID 1
curl -X POST http://localhost:8000/analyze/1

# View analysis results
curl http://localhost:8000/pull-requests/1/analysis
```

## Project Structure

```
pullsense/
├── backend/
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_analyzer.py    # AI integration logic
│   ├── tests/
│   │   ├── test_webhooks.py
│   │   └── test_full_flow.py
│   ├── main.py               # FastAPI application
│   ├── database.py           # SQLAlchemy models
│   ├── celery_app.py         # Celery task definitions
│   ├── config.py             # Configuration management
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment template
└── README.md
```

## Development Workflow

### Adding New Features

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Run tests: `pytest`
4. Commit changes: `git commit -m "Add your feature"`
5. Push branch: `git push origin feature/your-feature`

### Database Migrations

When modifying models:

```bash
# After changing models in database.py
python
>>> from database import Base, engine
>>> Base.metadata.create_all(bind=engine)
```

## Production Deployment

### Using Docker (coming soon)

```bash
docker-compose up -d
```

### Manual Deployment

1. Set up PostgreSQL instead of SQLite
2. Configure production environment variables
3. Use gunicorn instead of uvicorn:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
4. Set up process manager (systemd/supervisor)
5. Configure reverse proxy (nginx)

## Monitoring

### Check System Health

- Queue depth: Monitor Redis for pending jobs
- Worker status: Check Celery worker logs
- API health: `GET /health` endpoint
- Analysis metrics: `GET /stats` endpoint

### Performance Optimization

- Adjust Celery concurrency: `--concurrency=8`
- Implement caching for repeated PRs
- Use connection pooling for database
- Set rate limits for OpenAI API calls

## Troubleshooting

### Common Issues

**Celery not processing tasks**

- Ensure Redis is running: `redis-cli ping`
- Check Celery worker logs for errors
- Verify Redis URL in `.env`

**OpenAI errors**

- Check API key is valid
- Monitor rate limits
- System falls back to mock analysis automatically

**Module import errors**

- Ensure virtual environment is activated
- Check Python path in Celery worker
- Run `pip install -r requirements.txt`

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Future Enhancements

- [ ] Web UI for visualization
- [ ] Real GitHub API integration for code diffs
- [ ] Support for multiple AI providers
- [ ] Caching layer for cost optimization
- [ ] Webhook signature verification
- [ ] Multi-repository support
- [ ] Team collaboration features

## License

MIT License - see LICENSE file for details

## Author

Your Name - [Drew Dandrea](d.dandrea00@gmail.com)

## Acknowledgments

- Built with FastAPI, Celery, and OpenAI
- Inspired by modern code review tools
- Thanks to the open source community

```

```

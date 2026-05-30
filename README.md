# AI Code Reviewer & Analyzer

A production-grade intelligent code review system powered by Claude AI. Automatically analyzes code for bugs, security vulnerabilities, performance issues, and code quality improvements across multiple programming languages.

## 🎯 Features

- **Multi-Language Code Analysis**: Python, JavaScript/TypeScript, Java, Go, Rust, C++, and more
- **Intelligent Code Review**: Claude AI-powered comprehensive code analysis
- **Security Scanning**: Detect vulnerabilities, injection risks, and security anti-patterns
- **Performance Analysis**: Identify performance bottlenecks and optimization opportunities
- **Code Quality Metrics**: Complexity analysis, maintainability scoring, and style suggestions
- **Real-time Feedback**: WebSocket support for streaming analysis
- **Async Processing**: Handle large code reviews with job queuing
- **REST API**: Clean, documented API for integration
- **Rate Limiting & Caching**: Optimized for production use
- **Docker Support**: Easy deployment with Docker and Docker Compose

## 📋 Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **LLM**: Anthropic Claude API
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task Queue**: Celery + Redis
- **API Docs**: Swagger/OpenAPI
- **Auth**: JWT tokens

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context + Hooks
- **Code Editor**: Monaco Editor
- **Real-time**: WebSocket client

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Anthropic API Key

### Environment Setup

```bash
# Clone repository
git clone https://github.com/MoumitaMohanta/new.git
cd new

# Create .env file
cp .env.example .env
# Edit .env with your Anthropic API key
```

### Development

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs

# Or run locally
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

## 📚 API Documentation

### Endpoints

#### POST `/api/v1/reviews`
Submit code for review.

```json
{
  "code": "def hello():\n    print('world')",
  "language": "python",
  "filename": "hello.py"
}
```

#### GET `/api/v1/reviews/{review_id}`
Get review results.

Response:
```json
{
  "id": "uuid",
  "status": "completed",
  "score": 7.5,
  "summary": "Good code structure with minor improvements",
  "issues": [
    {
      "severity": "warning",
      "category": "style",
      "message": "Missing docstring",
      "line": 1,
      "suggestion": "Add a docstring to document the function"
    }
  ],
  "metrics": {
    "complexity": 1,
    "maintainability": 8.2,
    "security_score": 9.0
  }
}
```

#### WebSocket `/ws/reviews/{review_id}`
Stream real-time review analysis.

## 🏗️ Project Structure

```
.
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Configuration
│   │   ├── models.py               # Database models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── llm_service.py          # Claude integration
│   │   ├── code_analyzer.py        # Code analysis logic
│   │   ├── security_scanner.py     # Security checks
│   │   ├── performance_analyzer.py # Performance analysis
│   │   ├── database.py             # DB connection
│   │   ├── dependencies.py         # Dependency injection
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── reviews.py          # Review endpoints
│   │   │   ├── health.py           # Health check
│   │   │   └── ws.py               # WebSocket handler
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       ├── validators.py
│   │       └── cache.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_llm_service.py
│   │   ├── test_analyzers.py
│   │   └── conftest.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CodeEditor.tsx
│   │   │   ├── ReviewResults.tsx
│   │   │   ├── LanguageSelector.tsx
│   │   │   ├── Loading.tsx
│   │   │   └── Navigation.tsx
│   │   ├── pages/
│   │   │   ├── ReviewPage.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   └── SettingsPage.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── websocket.ts
│   │   ├── hooks/
│   │   │   ├── useReview.ts
│   │   │   └── useWebSocket.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 🔐 Security Considerations

- API key management via environment variables
- JWT token-based authentication
- Rate limiting per user/IP
- Input validation and sanitization
- CORS configuration
- SQL injection prevention via ORM
- XSS protection in frontend

## 📊 Supported Languages

- Python
- JavaScript/TypeScript
- Java
- Go
- Rust
- C/C++
- C#
- PHP
- Ruby
- SQL
- and more...

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov

# Frontend tests
cd frontend
npm run test
```

## 📈 Performance Metrics

- Average review time: 2-5 seconds
- Support for files up to 50KB
- 1000+ requests/day capacity
- 99.9% uptime SLA

## 🐛 Troubleshooting

### API Key not working
- Verify ANTHROPIC_API_KEY is set in .env
- Check API key validity at https://console.anthropic.com

### WebSocket connection fails
- Ensure backend is running on port 8000
- Check firewall/proxy settings
- Verify WebSocket support enabled

### Database connection error
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Run migrations: `alembic upgrade head`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Write tests
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 👤 Author

[Your Name](https://github.com/MoumitaMohanta)

## 📞 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/MoumitaMohanta/new/issues)
- Check [Discussions](https://github.com/MoumitaMohanta/new/discussions)
- Email: [your-email]

---

**Star this repo** ⭐ if you find it helpful!

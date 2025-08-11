# Insurge AI Backend

A comprehensive backend application built with FastAPI, featuring JWT authentication, PostgreSQL database, WebSocket chat functionality, and Docker containerization.

## 🚀 Quick Start

**Windows Users:**

```bash
setup-windows.bat
```

**Linux/macOS Users:**

```bash
chmod +x setup.sh
./setup.sh
```

**Manual Setup:** See [SETUP.md](SETUP.md) for detailed instructions.

**Docker Setup:**

```bash
docker-compose up --build
```

## 📋 Requirements

For development setup, you'll need the dependencies in `requirements.txt` (which includes all dev tools).
For production, use `requirements-prod.txt` (minimal dependencies only).

**Common Issues:**

- Import errors: Activate virtual environment first
- Permission errors on Windows: Use `--user` flag with pip
- Docker issues: Ensure Docker Desktop is running

## Features

- 🔐 **JWT Authentication** - Secure user authentication with access and refresh tokens
- 🐘 **PostgreSQL Integration** - Robust database with SQLAlchemy ORM
- 💬 **Real-time Chat** - WebSocket-powered chat functionality
- 🚀 **FastAPI Framework** - Modern, fast web framework for APIs
- 🐳 **Docker Support** - Full containerization with Docker Compose
- 📊 **Database Migrations** - Alembic for database schema management
- ✅ **Testing Suite** - Comprehensive tests with pytest
- 🔴 **Redis Support** - Caching and session management
- 📚 **API Documentation** - Automatic OpenAPI/Swagger documentation

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Migrations**: Alembic
- **Caching**: Redis
- **WebSockets**: Native FastAPI WebSocket support
- **Testing**: pytest
- **Containerization**: Docker & Docker Compose

## Project Structure

```
backend/
├── app/
│   ├── api/                    # API routes
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── users.py           # User management endpoints
│   │   ├── chat.py            # Chat session endpoints
│   │   └── dependencies.py    # FastAPI dependencies
│   ├── core/                  # Core configuration
│   │   ├── config.py          # Application settings
│   │   ├── database.py        # Database configuration
│   │   ├── security.py        # JWT and password handling
│   │   └── redis.py           # Redis configuration
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py            # User model
│   │   ├── chat_session.py    # Chat session model
│   │   └── chat_message.py    # Chat message model
│   ├── schemas/               # Pydantic schemas
│   │   ├── user.py            # User schemas
│   │   └── chat.py            # Chat schemas
│   ├── services/              # Business logic
│   │   ├── user_service.py    # User operations
│   │   └── chat_service.py    # Chat operations
│   ├── websockets/            # WebSocket functionality
│   │   ├── connection_manager.py  # WebSocket connection management
│   │   └── chat_handler.py        # Chat WebSocket handler
│   └── main.py               # FastAPI application
├── alembic/                   # Database migrations
├── tests/                     # Test suite
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                # Docker configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (if running locally)
- Redis (if running locally)

### Option 1: Docker Compose (Recommended)

1. Clone the repository:

```bash
git clone <repository-url>
cd backend
```

2. Start all services:

```bash
docker-compose up -d
```

3. The API will be available at:
   - **API**: http://localhost:8000
   - **Docs**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

### Option 2: Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your settings
```

3. Start PostgreSQL and Redis locally

4. Run database migrations:

```bash
alembic upgrade head
```

5. Start the application:

```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token

### Users

- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `DELETE /api/v1/users/me` - Deactivate current user

### Chat Sessions

- `POST /api/v1/chat/sessions` - Create new chat session
- `GET /api/v1/chat/sessions` - Get user's chat sessions
- `GET /api/v1/chat/sessions/{id}` - Get specific chat session
- `PUT /api/v1/chat/sessions/{id}` - Update chat session
- `DELETE /api/v1/chat/sessions/{id}` - Delete chat session

### Chat Messages

- `POST /api/v1/chat/sessions/{id}/messages` - Add message to session
- `GET /api/v1/chat/sessions/{id}/messages` - Get session messages

### WebSocket

- `WS /ws?token={jwt_token}&session_id={session_id}` - Real-time chat

## WebSocket Usage

Connect to the WebSocket endpoint with a valid JWT token:

```javascript
const ws = new WebSocket(
  "ws://localhost:8000/ws?token=YOUR_JWT_TOKEN&session_id=123"
);

// Send a message
ws.send(
  JSON.stringify({
    type: "chat_message",
    content: "Hello, world!",
    session_id: 123,
  })
);

// Listen for messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Received:", message);
};
```

## Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback migrations:

```bash
alembic downgrade -1
```

## Testing

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_auth.py
```

## Environment Variables

| Variable                      | Description                  | Default                                                                |
| ----------------------------- | ---------------------------- | ---------------------------------------------------------------------- |
| `DATABASE_URL`                | PostgreSQL connection string | `postgresql://insurge_user:insurge_password@localhost:5432/insurge_db` |
| `REDIS_URL`                   | Redis connection string      | `redis://localhost:6379`                                               |
| `SECRET_KEY`                  | JWT secret key               | `your-super-secret-key-change-this-in-production`                      |
| `ALGORITHM`                   | JWT algorithm                | `HS256`                                                                |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration      | `30`                                                                   |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Refresh token expiration     | `7`                                                                    |

## Production Deployment

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong, random value
- [ ] Use environment variables for all sensitive data
- [ ] Enable HTTPS in production
- [ ] Configure proper CORS origins
- [ ] Set up proper database backups
- [ ] Configure logging and monitoring
- [ ] Use a reverse proxy (nginx)
- [ ] Set up database connection pooling

### Docker Production

1. Build production image:

```bash
docker build -t insurge-backend .
```

2. Run with production environment:

```bash
docker run -d \
  -e DATABASE_URL=your-production-db-url \
  -e SECRET_KEY=your-production-secret \
  -e ENVIRONMENT=production \
  -p 8000:8000 \
  insurge-backend
```

## API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Make sure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please create an issue in the repository or contact the development team.

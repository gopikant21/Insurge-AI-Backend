# Insurge AI Backend

A comprehensive backend application built with FastAPI, featuring JWT authentication, PostgreSQL database, **enhanced multi-user chat system**, WebSocket functionality, and Docker containerization.

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

## ⚙️ Environment Configuration

### Quick Setup

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Generate a secure secret key:

   ```bash
   python generate_secret_key.py
   ```

3. Update the `.env` file with your configuration values.

### Key Environment Variables

| Variable                | Description                    | Default                     | Required |
| ----------------------- | ------------------------------ | --------------------------- | -------- |
| `DATABASE_URL`          | PostgreSQL connection string   | `postgresql://...`          | ✅       |
| `REDIS_URL`             | Redis connection string        | `redis://localhost:6379`    | ✅       |
| `SECRET_KEY`            | JWT secret key                 | `change-this-in-production` | ✅       |
| `OPENAI_API_KEY`        | OpenAI API key for AI features | -                           | ⚠️       |
| `DEBUG`                 | Enable debug mode              | `true`                      | ❌       |
| `MAX_CHAT_PARTICIPANTS` | Max users per chat session     | `50`                        | ❌       |
| `ALLOWED_ORIGINS`       | CORS allowed origins           | `["http://localhost:3000"]` | ❌       |

### Production Configuration

For production deployment, ensure you:

- Set `DEBUG=false`
- Set `ENVIRONMENT=production`
- Use a strong `SECRET_KEY` (64+ characters)
- Configure proper database and Redis URLs
- Set appropriate `ALLOWED_ORIGINS`
- Enable SSL/TLS

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
- 💬 **Enhanced Multi-User Chat System** - Advanced chat with role-based permissions, public/private rooms, and participant management
- 🚀 **FastAPI Framework** - Modern, fast web framework for APIs
- 🐳 **Docker Support** - Full containerization with Docker Compose
- 📊 **Database Migrations** - Alembic for database schema management
- ✅ **Testing Suite** - Comprehensive tests with pytest
- 🔴 **Redis Support** - Caching and session management
- 📚 **API Documentation** - Automatic OpenAPI/Swagger documentation
- 🌐 **Real-time WebSockets** - Live chat functionality
- 👥 **Role-Based Access Control** - Owner, Admin, Member, Viewer permissions
- 🏢 **Session Management** - Create, join, leave, and manage chat rooms

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
│   │   ├── chat.py            # Enhanced multi-user chat endpoints
│   │   └── dependencies.py    # FastAPI dependencies
│   ├── core/                  # Core configuration
│   │   ├── config.py          # Application settings
│   │   ├── database.py        # Database configuration
│   │   ├── security.py        # JWT and password handling
│   │   └── redis.py           # Redis configuration
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py            # User model
│   │   ├── chat_session.py    # Enhanced chat session model with multi-user support
│   │   ├── chat_message.py    # Chat message model with user attribution
│   │   └── chat_participant.py # Chat participant model for role management
│   ├── schemas/               # Pydantic schemas
│   │   ├── user.py            # User schemas
│   │   └── chat.py            # Enhanced chat schemas with participant management
│   ├── services/              # Business logic
│   │   ├── user_service.py    # User operations
│   │   ├── chat_service.py    # Enhanced chat operations with multi-user support
│   │   └── ai_service.py      # AI integration service
│   ├── websockets/            # WebSocket functionality
│   │   ├── connection_manager.py  # WebSocket connection management
│   │   └── chat_handler.py        # Enhanced chat WebSocket handler
│   └── main.py               # FastAPI application
├── alembic/                   # Database migrations
│   └── versions/              # Migration files including multi-user chat migration
├── tests/                     # Test suite
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                # Docker configuration
├── requirements.txt          # Python dependencies
├── ENHANCED_CHAT_API.md      # Comprehensive API documentation for chat system
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

### Enhanced Chat Sessions

- `POST /api/v1/chat/sessions` - Create new chat session (private/public/invite-only)
- `GET /api/v1/chat/sessions` - Get user's chat sessions
- `GET /api/v1/chat/sessions/public` - Get public sessions available to join
- `GET /api/v1/chat/sessions/{id}` - Get specific chat session with participants
- `PUT /api/v1/chat/sessions/{id}` - Update chat session (owner/admin only)
- `DELETE /api/v1/chat/sessions/{id}` - Delete chat session (owner only)

### Participant Management

- `POST /api/v1/chat/sessions/{id}/join` - Join a public chat session
- `POST /api/v1/chat/sessions/{id}/leave` - Leave a chat session
- `POST /api/v1/chat/sessions/{id}/invite` - Invite user to session (owner/admin)
- `PUT /api/v1/chat/sessions/{id}/participants/{user_id}/role` - Update participant role
- `DELETE /api/v1/chat/sessions/{id}/participants/{user_id}` - Remove participant
- `GET /api/v1/chat/sessions/{id}/participants` - Get session participants

### Chat Messages

- `POST /api/v1/chat/sessions/{id}/messages` - Add message to session
- `GET /api/v1/chat/sessions/{id}/messages` - Get session messages with user attribution

### WebSocket

- `WS /ws?token={jwt_token}&session_id={session_id}` - Real-time chat with multi-user support

## Multi-User Chat System

### 🎯 Key Features

- **Session Types**: Create private, public, or invite-only chat rooms
- **Role-Based Permissions**: Owner, Admin, Member, and Viewer roles with different capabilities
- **Participant Management**: Invite users, manage roles, and remove participants
- **Public Room Discovery**: Browse and join public chat rooms
- **User Attribution**: All messages show who sent them
- **Real-time Updates**: WebSocket support for live messaging

### 🔐 Permission Matrix

| Action              | Owner | Admin | Member | Viewer |
| ------------------- | ----- | ----- | ------ | ------ |
| View messages       | ✅    | ✅    | ✅     | ✅     |
| Send messages       | ✅    | ✅    | ✅     | ❌     |
| Update session      | ✅    | ✅    | ❌     | ❌     |
| Delete session      | ✅    | ❌    | ❌     | ❌     |
| Invite users        | ✅    | ✅    | ❌     | ❌     |
| Remove participants | ✅    | ✅    | ❌     | ❌     |
| Change roles        | ✅    | ✅\*  | ❌     | ❌     |

\*Admins can change roles but cannot promote to owner or modify owner's role.

### 📋 Session Types

- **Private**: Only owner can access, perfect for personal notes or small team discussions
- **Public**: Anyone can discover and join, ideal for community discussions
- **Invite-Only**: Only invited users can join, great for controlled group discussions

### 🚀 Quick Chat Example

```python
# Create a public chat room
session_data = {
    "title": "General Discussion",
    "description": "Open chat for everyone",
    "session_type": "public",
    "max_participants": 50
}

# Join a public room
POST /api/v1/chat/sessions/{id}/join

# Send a message
message_data = {
    "role": "user",
    "content": "Hello everyone!"
}
```

For complete API documentation, see [ENHANCED_CHAT_API.md](ENHANCED_CHAT_API.md).

## WebSocket Usage

Connect to the WebSocket endpoint with a valid JWT token for real-time multi-user chat:

```javascript
const ws = new WebSocket(
  "ws://localhost:8000/ws?token=YOUR_JWT_TOKEN&session_id=123"
);

// Send a message (with user attribution)
ws.send(
  JSON.stringify({
    type: "chat_message",
    content: "Hello, world!",
    session_id: 123,
  })
);

// Listen for messages (includes sender information)
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(`${message.username}: ${message.content}`);
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

## Testing the Enhanced Chat System

### Run Comprehensive Tests

Test the complete multi-user chat functionality:

```bash
python test_enhanced_chat_api.py
```

### Run Simple API Test

Quick test of basic functionality:

```bash
python simple_test.py
```

### Run Unit Tests

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
- **Enhanced Chat API Guide**: [ENHANCED_CHAT_API.md](ENHANCED_CHAT_API.md)

## Recent Updates

### 🆕 Enhanced Multi-User Chat System (v2.0)

We've completely overhauled the chat system with advanced multi-user capabilities:

- ✨ **Role-based permissions** with Owner, Admin, Member, Viewer roles
- 🏠 **Session types**: Private, Public, and Invite-only rooms
- 👥 **Participant management**: Invite, remove, and manage user roles
- 🌐 **Public room discovery**: Browse and join community discussions
- 📝 **User attribution**: All messages now show who sent them
- 🔒 **Enhanced security**: Proper authorization for all actions
- 📊 **Better analytics**: Participant and message counts
- 🔄 **Database migration**: Seamless upgrade with Alembic

### Migration Applied

The database has been updated with new tables and relationships:

- `chat_participants` - Role-based user participation
- Enhanced `chat_sessions` with session types and limits
- Updated `chat_messages` with user attribution

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

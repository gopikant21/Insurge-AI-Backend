from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager

import os

from app.core.config import settings
from app.core.database import engine, Base, get_db, SessionLocal
from app.core.redis import redis_manager
from app.api import auth, users, chat
from app.websockets.chat_handler import websocket_endpoint



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await redis_manager.connect()
        
        # Test database connection
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            db_status = "Connected ✅"
            # CREATE DATABASE TABLES - Add this section
            print("🔧 Creating database tables...")
            Base.metadata.create_all(bind=engine)
            print("✅ Database tables created successfully!")
        except Exception as db_error:
            db_status = f"Failed ❌: {str(db_error)}"
        finally:
            db.close()
        
        # Test Redis connection
        try:
            await redis_manager.get("test")
            redis_status = "Connected ✅"
        except Exception as redis_error:
            redis_status = f"Failed ❌: {str(redis_error)}"
        
        print("🚀 Application started successfully!")
        print(f"📊 Environment: {settings.environment}")
        print(f"🔗 Database: {db_status}")
        print(f"🔴 Redis: {redis_status}")
        
    except Exception as e:
        print(f"❌ Startup failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    await redis_manager.disconnect()
    print("👋 Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Insurge AI Backend",
    description="A comprehensive backend API with JWT authentication, PostgreSQL, and WebSocket chat functionality",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        settings.allowed_origins + ["*"] if settings.debug else settings.allowed_origins
    ),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))

        # Test Redis connection
        await redis_manager.get("health_check")

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "database": "connected",
                "redis": "connected",
                "environment": settings.environment,
                "version": "1.0.0",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "environment": settings.environment,
                "version": "1.0.0",
            },
        )


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Insurge AI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    token: str,
    session_id: int = None,
    db: Session = Depends(get_db),
):
    """WebSocket endpoint for real-time chat."""
    await websocket_endpoint(websocket, token, session_id, db)


# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Endpoint not found"})


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )

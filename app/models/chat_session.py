from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class SessionType(enum.Enum):
    PRIVATE = "private"  # Only owner can access
    PUBLIC = "public"  # Anyone can join
    INVITE_ONLY = "invite_only"  # Only invited users can join


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, default="New Chat")
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Owner
    session_type = Column(
        Enum(SessionType), default=SessionType.PRIVATE, nullable=False
    )
    max_participants = Column(Integer, default=10)  # Maximum number of participants
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    owner = relationship("User", backref="owned_chat_sessions")
    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )
    participants = relationship(
        "ChatParticipant", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<ChatSession(id={self.id}, title={self.title}, user_id={self.user_id})>"
        )

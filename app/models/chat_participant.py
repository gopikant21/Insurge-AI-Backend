from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ParticipantRole(enum.Enum):
    OWNER = "owner"  # User who created the session
    ADMIN = "admin"  # Can manage the session
    MEMBER = "member"  # Can send messages
    VIEWER = "viewer"  # Can only view messages


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(ParticipantRole), default=ParticipantRole.MEMBER, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    session = relationship("ChatSession", back_populates="participants")
    user = relationship("User", backref="chat_participations")

    def __repr__(self):
        return f"<ChatParticipant(session_id={self.session_id}, user_id={self.user_id}, role={self.role})>"

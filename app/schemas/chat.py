from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.chat_message import MessageRole
from app.models.chat_session import SessionType
from app.models.chat_participant import ParticipantRole


class ChatSessionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    session_type: SessionType = Field(default=SessionType.PRIVATE)
    max_participants: int = Field(default=10, ge=2, le=100)


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    session_type: Optional[SessionType] = None
    max_participants: Optional[int] = Field(None, ge=2, le=100)


class ChatParticipantBase(BaseModel):
    role: ParticipantRole = ParticipantRole.MEMBER


class ChatParticipantResponse(ChatParticipantBase):
    id: int
    user_id: int
    username: Optional[str] = None  # Will be populated from user relationship
    joined_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    role: MessageRole
    content: str = Field(..., min_length=1)


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: int
    session_id: int
    user_id: Optional[int] = None
    username: Optional[str] = None  # Will be populated from user relationship
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(ChatSessionBase):
    id: int
    user_id: int
    owner_username: Optional[str] = None  # Will be populated from owner relationship
    is_active: bool
    created_at: datetime
    updated_at: datetime
    participants: List[ChatParticipantResponse] = []
    messages: List[ChatMessageResponse] = []
    participant_count: int = 0

    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    session_type: SessionType
    owner_username: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    participant_count: int = 0

    class Config:
        from_attributes = True


class JoinSessionRequest(BaseModel):
    pass  # No additional fields needed for joining


class InviteUserRequest(BaseModel):
    user_id: int
    role: ParticipantRole = ParticipantRole.MEMBER


class UpdateParticipantRoleRequest(BaseModel):
    role: ParticipantRole


class PublicSessionsResponse(BaseModel):
    sessions: List[ChatSessionListResponse]
    total: int


class WebSocketMessage(BaseModel):
    type: str  # "chat_message", "system_message", etc.
    content: str
    session_id: Optional[int] = None
    timestamp: Optional[datetime] = None

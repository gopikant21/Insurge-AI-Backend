from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.dependencies import get_current_active_user
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatParticipantResponse,
    JoinSessionRequest,
    InviteUserRequest,
    UpdateParticipantRoleRequest,
    PublicSessionsResponse,
)
from app.services.chat_service import ChatService
from app.models.user import User
from app.models.chat_participant import ParticipantRole

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED
)
def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new chat session."""
    chat_service = ChatService(db)
    session = chat_service.create_session(current_user.id, session_data)

    # Get the session with all details to return
    detailed_session = chat_service.get_session_with_details(
        session.id, current_user.id
    )
    if not detailed_session:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created session",
        )

    # Format the response
    return _format_session_response(detailed_session)


@router.get("/sessions", response_model=List[ChatSessionListResponse])
def get_chat_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all chat sessions where the current user is a participant."""
    chat_service = ChatService(db)
    sessions_with_counts = chat_service.get_user_sessions_with_counts(
        current_user.id, skip=skip, limit=limit
    )

    result = []
    for session, message_count, participant_count in sessions_with_counts:
        result.append(
            ChatSessionListResponse(
                id=session.id,
                title=session.title,
                description=session.description,
                session_type=session.session_type,
                owner_username=session.owner.username if session.owner else None,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=message_count or 0,
                participant_count=participant_count or 0,
            )
        )

    return result


@router.get("/sessions/public", response_model=PublicSessionsResponse)
def get_public_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get public chat sessions that the user can join."""
    chat_service = ChatService(db)
    sessions, total = chat_service.get_public_sessions(
        current_user.id, skip=skip, limit=limit
    )

    formatted_sessions = []
    for session in sessions:
        # Get participant count for each session
        from app.models.chat_participant import ChatParticipant

        participant_count = (
            db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session.id,
                ChatParticipant.is_active == True,
            )
            .count()
        )

        formatted_sessions.append(
            ChatSessionListResponse(
                id=session.id,
                title=session.title,
                description=session.description,
                session_type=session.session_type,
                owner_username=session.owner.username if session.owner else None,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=0,  # We don't need message count for public sessions list
                participant_count=participant_count,
            )
        )

    return PublicSessionsResponse(sessions=formatted_sessions, total=total)


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific chat session with messages and participants."""
    chat_service = ChatService(db)
    session = chat_service.get_session_with_details(session_id, current_user.id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    return _format_session_response(session)


@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
def update_chat_session(
    session_id: int,
    session_update: ChatSessionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a chat session (owner/admin only)."""
    chat_service = ChatService(db)
    session = chat_service.update_session(session_id, current_user.id, session_update)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or insufficient permissions",
        )

    # Get the updated session with all details
    detailed_session = chat_service.get_session_with_details(
        session_id, current_user.id
    )
    return _format_session_response(detailed_session)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a chat session (owner only)."""
    chat_service = ChatService(db)
    success = chat_service.delete_session(session_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or insufficient permissions",
        )

    return None


@router.post("/sessions/{session_id}/join", response_model=dict)
def join_chat_session(
    session_id: int,
    join_data: JoinSessionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Join a public chat session."""
    chat_service = ChatService(db)
    participant = chat_service.join_session(session_id, current_user.id)

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot join session. Session may not exist, be private, or at capacity.",
        )

    return {
        "message": "Successfully joined the chat session",
        "participant_id": participant.id,
    }


@router.post("/sessions/{session_id}/leave", response_model=dict)
def leave_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Leave a chat session."""
    chat_service = ChatService(db)
    success = chat_service.leave_session(session_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot leave session. You may not be a participant or may be the owner.",
        )

    return {"message": "Successfully left the chat session"}


@router.post("/sessions/{session_id}/invite", response_model=ChatParticipantResponse)
def invite_user_to_session(
    session_id: int,
    invite_data: InviteUserRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Invite a user to a chat session (owner/admin only)."""
    chat_service = ChatService(db)
    participant = chat_service.invite_user(session_id, current_user.id, invite_data)

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot invite user. Check permissions, user existence, and session capacity.",
        )

    return ChatParticipantResponse(
        id=participant.id,
        user_id=participant.user_id,
        username=participant.user.username if participant.user else None,
        role=participant.role,
        joined_at=participant.joined_at,
        is_active=participant.is_active,
    )


@router.put(
    "/sessions/{session_id}/participants/{user_id}/role",
    response_model=ChatParticipantResponse,
)
def update_participant_role(
    session_id: int,
    user_id: int,
    role_data: UpdateParticipantRoleRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a participant's role (owner/admin only)."""
    chat_service = ChatService(db)
    participant = chat_service.update_participant_role(
        session_id, current_user.id, user_id, role_data
    )

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update participant role. Check permissions and participant existence.",
        )

    return ChatParticipantResponse(
        id=participant.id,
        user_id=participant.user_id,
        username=participant.user.username if participant.user else None,
        role=participant.role,
        joined_at=participant.joined_at,
        is_active=participant.is_active,
    )


@router.delete("/sessions/{session_id}/participants/{user_id}", response_model=dict)
def remove_participant(
    session_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove a participant from a chat session (owner/admin only)."""
    chat_service = ChatService(db)
    success = chat_service.remove_participant(session_id, current_user.id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove participant. Check permissions and participant existence.",
        )

    return {"message": "Participant removed successfully"}


@router.get(
    "/sessions/{session_id}/participants", response_model=List[ChatParticipantResponse]
)
def get_session_participants(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all participants in a chat session."""
    chat_service = ChatService(db)
    session = chat_service.get_session_with_details(session_id, current_user.id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    participants = []
    for participant in session.participants:
        if participant.is_active:
            participants.append(
                ChatParticipantResponse(
                    id=participant.id,
                    user_id=participant.user_id,
                    username=participant.user.username if participant.user else None,
                    role=participant.role,
                    joined_at=participant.joined_at,
                    is_active=participant.is_active,
                )
            )

    return participants


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_message_to_session(
    session_id: int,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Add a message to a chat session."""
    chat_service = ChatService(db)
    message = chat_service.add_message(session_id, current_user.id, message_data)

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or insufficient permissions",
        )

    return ChatMessageResponse(
        id=message.id,
        session_id=message.session_id,
        user_id=message.user_id,
        username=message.user.username if message.user else None,
        role=message.role,
        content=message.content,
        created_at=message.created_at,
    )


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_session_messages(
    session_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get messages for a chat session."""
    chat_service = ChatService(db)
    messages = chat_service.get_session_messages(
        session_id, current_user.id, skip=skip, limit=limit
    )

    formatted_messages = []
    for message in messages:
        formatted_messages.append(
            ChatMessageResponse(
                id=message.id,
                session_id=message.session_id,
                user_id=message.user_id,
                username=message.user.username if message.user else None,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
        )

    return formatted_messages


def _format_session_response(session) -> ChatSessionResponse:
    """Helper function to format session response with all details."""
    participants = []
    for participant in session.participants:
        if participant.is_active:
            participants.append(
                ChatParticipantResponse(
                    id=participant.id,
                    user_id=participant.user_id,
                    username=participant.user.username if participant.user else None,
                    role=participant.role,
                    joined_at=participant.joined_at,
                    is_active=participant.is_active,
                )
            )

    messages = []
    for message in session.messages:
        messages.append(
            ChatMessageResponse(
                id=message.id,
                session_id=message.session_id,
                user_id=message.user_id,
                username=message.user.username if message.user else None,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
        )

    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        description=session.description,
        session_type=session.session_type,
        max_participants=session.max_participants,
        user_id=session.user_id,
        owner_username=session.owner.username if session.owner else None,
        is_active=session.is_active,
        created_at=session.created_at,
        updated_at=session.updated_at,
        participants=participants,
        messages=messages,
        participant_count=len(participants),
    )

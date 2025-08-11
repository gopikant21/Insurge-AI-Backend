from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, and_, or_
from app.models.chat_session import ChatSession, SessionType
from app.models.chat_message import ChatMessage, MessageRole
from app.models.chat_participant import ChatParticipant, ParticipantRole
from app.models.user import User
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatMessageCreate,
    InviteUserRequest,
    UpdateParticipantRoleRequest,
)


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(
        self, user_id: int, session_data: ChatSessionCreate
    ) -> ChatSession:
        """Create a new chat session."""
        db_session = ChatSession(
            title=session_data.title,
            description=session_data.description,
            user_id=user_id,
            session_type=session_data.session_type,
            max_participants=session_data.max_participants,
        )

        self.db.add(db_session)
        self.db.flush()  # Get the session ID

        # Add the owner as a participant with owner role
        owner_participant = ChatParticipant(
            session_id=db_session.id, user_id=user_id, role=ParticipantRole.OWNER
        )
        self.db.add(owner_participant)

        self.db.commit()
        self.db.refresh(db_session)
        return db_session

    def get_user_sessions(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChatSession]:
        """Get all chat sessions where user is a participant."""
        return (
            self.db.query(ChatSession)
            .join(ChatParticipant)
            .filter(
                ChatParticipant.user_id == user_id,
                ChatParticipant.is_active == True,
                ChatSession.is_active == True,
            )
            .order_by(desc(ChatSession.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_public_sessions(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[ChatSession], int]:
        """Get public chat sessions that user can join."""
        # Get sessions where user is not already a participant
        subquery = (
            self.db.query(ChatParticipant.session_id)
            .filter(
                ChatParticipant.user_id == user_id, ChatParticipant.is_active == True
            )
            .subquery()
        )

        sessions = (
            self.db.query(ChatSession)
            .filter(
                ChatSession.session_type == SessionType.PUBLIC,
                ChatSession.is_active == True,
                ~ChatSession.id.in_(subquery),
            )
            .order_by(desc(ChatSession.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        total = (
            self.db.query(ChatSession)
            .filter(
                ChatSession.session_type == SessionType.PUBLIC,
                ChatSession.is_active == True,
                ~ChatSession.id.in_(subquery),
            )
            .count()
        )

        return sessions, total

    def get_session_by_id(self, session_id: int, user_id: int) -> Optional[ChatSession]:
        """Get a specific chat session if user has access."""
        return (
            self.db.query(ChatSession)
            .join(ChatParticipant)
            .filter(
                ChatSession.id == session_id,
                ChatParticipant.user_id == user_id,
                ChatParticipant.is_active == True,
                ChatSession.is_active == True,
            )
            .first()
        )

    def get_session_with_details(
        self, session_id: int, user_id: int
    ) -> Optional[ChatSession]:
        """Get a chat session with all details (participants and messages)."""
        return (
            self.db.query(ChatSession)
            .options(
                joinedload(ChatSession.participants).joinedload(ChatParticipant.user),
                joinedload(ChatSession.messages).joinedload(ChatMessage.user),
                joinedload(ChatSession.owner),
            )
            .join(ChatParticipant)
            .filter(
                ChatSession.id == session_id,
                ChatParticipant.user_id == user_id,
                ChatParticipant.is_active == True,
                ChatSession.is_active == True,
            )
            .first()
        )

    def update_session(
        self, session_id: int, user_id: int, session_data: ChatSessionUpdate
    ) -> Optional[ChatSession]:
        """Update a chat session (only owner or admin can update)."""
        # Check if user has permission to update
        participant = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.user_id == user_id,
                ChatParticipant.is_active == True,
                ChatParticipant.role.in_(
                    [ParticipantRole.OWNER, ParticipantRole.ADMIN]
                ),
            )
            .first()
        )

        if not participant:
            return None

        session = (
            self.db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.is_active == True)
            .first()
        )

        if not session:
            return None

        update_data = session_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)

        self.db.commit()
        self.db.refresh(session)
        return session

    def delete_session(self, session_id: int, user_id: int) -> bool:
        """Soft delete a chat session (only owner can delete)."""
        session = (
            self.db.query(ChatSession)
            .filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,  # Only owner can delete
                ChatSession.is_active == True,
            )
            .first()
        )

        if not session:
            return False

        session.is_active = False
        self.db.commit()
        return True

    def join_session(self, session_id: int, user_id: int) -> Optional[ChatParticipant]:
        """Join a public chat session."""
        session = (
            self.db.query(ChatSession)
            .filter(
                ChatSession.id == session_id,
                ChatSession.is_active == True,
                ChatSession.session_type.in_([SessionType.PUBLIC]),
            )
            .first()
        )

        if not session:
            return None

        # Check if user is already a participant
        existing_participant = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.user_id == user_id,
            )
            .first()
        )

        if existing_participant:
            if not existing_participant.is_active:
                existing_participant.is_active = True
                self.db.commit()
                return existing_participant
            return existing_participant

        # Check participant limit
        current_participants = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.is_active == True,
            )
            .count()
        )

        if current_participants >= session.max_participants:
            return None

        # Add new participant
        participant = ChatParticipant(
            session_id=session_id, user_id=user_id, role=ParticipantRole.MEMBER
        )

        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def leave_session(self, session_id: int, user_id: int) -> bool:
        """Leave a chat session."""
        participant = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.user_id == user_id,
                ChatParticipant.is_active == True,
            )
            .first()
        )

        if not participant:
            return False

        # Owner cannot leave their own session
        if participant.role == ParticipantRole.OWNER:
            return False

        participant.is_active = False
        self.db.commit()
        return True

    def invite_user(
        self, session_id: int, inviter_id: int, invite_data: InviteUserRequest
    ) -> Optional[ChatParticipant]:
        """Invite a user to a chat session (owner/admin only)."""
        # Check if inviter has permission
        inviter_participant = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.user_id == inviter_id,
                ChatParticipant.is_active == True,
                ChatParticipant.role.in_(
                    [ParticipantRole.OWNER, ParticipantRole.ADMIN]
                ),
            )
            .first()
        )

        if not inviter_participant:
            return None

        # Check if session exists and is active
        session = (
            self.db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.is_active == True)
            .first()
        )

        if not session:
            return None

        # Check if user exists
        user_exists = (
            self.db.query(User)
            .filter(User.id == invite_data.user_id, User.is_active == True)
            .first()
        )

        if not user_exists:
            return None

        # Check if user is already a participant
        existing_participant = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.user_id == invite_data.user_id,
            )
            .first()
        )

        if existing_participant:
            if not existing_participant.is_active:
                existing_participant.is_active = True
                existing_participant.role = invite_data.role
                self.db.commit()
                return existing_participant
            return existing_participant

        # Check participant limit
        current_participants = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.is_active == True,
            )
            .count()
        )

        if current_participants >= session.max_participants:
            return None

        # Add new participant
        participant = ChatParticipant(
            session_id=session_id, user_id=invite_data.user_id, role=invite_data.role
        )

        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def update_participant_role(
        self,
        session_id: int,
        admin_id: int,
        participant_user_id: int,
        role_data: UpdateParticipantRoleRequest,
    ) -> Optional[ChatParticipant]:
        """Update a participant's role (owner/admin only)."""
        # Check if admin has permission
        admin_participant = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.user_id == admin_id,
                ChatParticipant.is_active == True,
                ChatParticipant.role.in_(
                    [ParticipantRole.OWNER, ParticipantRole.ADMIN]
                ),
            )
            .first()
        )

        if not admin_participant:
            return None

        # Get the participant to update
        participant = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.user_id == participant_user_id,
                ChatParticipant.is_active == True,
            )
            .first()
        )

        if not participant:
            return None

        # Cannot change owner role or make someone owner (unless admin is owner)
        if (
            participant.role == ParticipantRole.OWNER
            or role_data.role == ParticipantRole.OWNER
        ):
            if admin_participant.role != ParticipantRole.OWNER:
                return None

        participant.role = role_data.role
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def remove_participant(
        self, session_id: int, admin_id: int, participant_user_id: int
    ) -> bool:
        """Remove a participant from session (owner/admin only)."""
        # Check if admin has permission
        admin_participant = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.user_id == admin_id,
                ChatParticipant.is_active == True,
                ChatParticipant.role.in_(
                    [ParticipantRole.OWNER, ParticipantRole.ADMIN]
                ),
            )
            .first()
        )

        if not admin_participant:
            return False

        # Get the participant to remove
        participant = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.user_id == participant_user_id,
                ChatParticipant.is_active == True,
            )
            .first()
        )

        if not participant:
            return False

        # Cannot remove owner
        if participant.role == ParticipantRole.OWNER:
            return False

        participant.is_active = False
        self.db.commit()
        return True

    def add_message(
        self, session_id: int, user_id: int, message_data: ChatMessageCreate
    ) -> Optional[ChatMessage]:
        """Add a message to a chat session."""
        # Check if user is a participant with message permissions
        participant = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.user_id == user_id,
                ChatParticipant.is_active == True,
                ChatParticipant.role.in_(
                    [
                        ParticipantRole.OWNER,
                        ParticipantRole.ADMIN,
                        ParticipantRole.MEMBER,
                    ]
                ),
            )
            .first()
        )

        if not participant:
            return None

        db_message = ChatMessage(
            session_id=session_id,
            user_id=user_id,
            role=message_data.role,
            content=message_data.content,
        )

        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def get_session_messages(
        self, session_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChatMessage]:
        """Get messages for a chat session."""
        # Check if user is a participant
        participant = (
            self.db.query(ChatParticipant)
            .filter(
                ChatParticipant.session_id == session_id,
                ChatParticipant.user_id == user_id,
                ChatParticipant.is_active == True,
            )
            .first()
        )

        if not participant:
            return []

        return (
            self.db.query(ChatMessage)
            .options(joinedload(ChatMessage.user))
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_sessions_with_counts(
        self, user_id: int, skip: int = 0, limit: int = 100
    ):
        """Get user sessions with message and participant counts."""
        # Create an alias for the participant table to avoid conflicts
        from sqlalchemy.orm import aliased

        participant_alias = aliased(ChatParticipant)

        return (
            self.db.query(
                ChatSession,
                func.count(ChatMessage.id.distinct()).label("message_count"),
                func.count(ChatParticipant.id.distinct()).label("participant_count"),
            )
            .outerjoin(ChatMessage, ChatSession.id == ChatMessage.session_id)
            .outerjoin(
                ChatParticipant,
                and_(
                    ChatSession.id == ChatParticipant.session_id,
                    ChatParticipant.is_active == True,
                ),
            )
            .join(
                participant_alias,
                and_(  # Join for user's participation
                    ChatSession.id == participant_alias.session_id,
                    participant_alias.user_id == user_id,
                    participant_alias.is_active == True,
                ),
            )
            .options(joinedload(ChatSession.owner))
            .filter(ChatSession.is_active == True)
            .group_by(ChatSession.id)
            .order_by(desc(ChatSession.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

from fastapi import WebSocket, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.services.user_service import UserService
from app.services.chat_service import ChatService
from app.websockets.connection_manager import manager
from app.models.chat_message import MessageRole
from app.schemas.chat import ChatMessageCreate, WebSocketMessage
import json
import asyncio
from datetime import datetime
from typing import Optional


async def get_user_from_token(token: str, db: Session):
    """Get user from WebSocket token."""
    try:
        payload = verify_token(token)
        if not payload:
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)

        if not user or not user.is_active:
            return None

        return user
    except Exception:
        return None


async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    session_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """WebSocket endpoint for chat functionality."""
    # Authenticate user
    user = await get_user_from_token(token, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Validate session if provided
    if session_id:
        chat_service = ChatService(db)
        session = chat_service.get_session_by_id(session_id, user.id)
        if not session:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    # Connect to WebSocket
    await manager.connect(websocket, user.id, session_id)

    try:
        # Send welcome message
        welcome_message = WebSocketMessage(
            type="system_message",
            content=f"Connected to chat{'session ' + str(session_id) if session_id else ''}",
            session_id=session_id,
            timestamp=datetime.utcnow(),
        )
        await manager.send_personal_message(welcome_message.json(), websocket)

        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)
                message_type = message_data.get("type", "chat_message")
                content = message_data.get("content", "")
                target_session_id = message_data.get("session_id", session_id)

                if message_type == "chat_message" and content and target_session_id:
                    # Validate session ownership
                    chat_service = ChatService(db)
                    session = chat_service.get_session_by_id(target_session_id, user.id)
                    if not session:
                        error_message = WebSocketMessage(
                            type="error",
                            content="Session not found or access denied",
                            timestamp=datetime.utcnow(),
                        )
                        await manager.send_personal_message(
                            error_message.json(), websocket
                        )
                        continue

                    # Save user message to database
                    user_message = ChatMessageCreate(
                        role=MessageRole.USER, content=content
                    )
                    saved_message = chat_service.add_message(
                        target_session_id, user.id, user_message
                    )

                    if saved_message:
                        # Broadcast user message to session
                        user_msg = WebSocketMessage(
                            type="chat_message",
                            content=content,
                            session_id=target_session_id,
                            timestamp=saved_message.created_at,
                        )
                        await manager.send_message_to_session(
                            user_msg.json(), user.id, target_session_id
                        )

                        # Get conversation history for better AI responses
                        messages = chat_service.get_session_messages(
                            target_session_id, user.id, limit=10
                        )
                        conversation_history = [
                            {"role": msg.role.value.lower(), "content": msg.content}
                            for msg in messages
                        ]

                        # Simulate AI response with conversation context
                        ai_response = await generate_ai_response(
                            content, conversation_history
                        )

                        # Save AI response to database
                        ai_message = ChatMessageCreate(
                            role=MessageRole.ASSISTANT, content=ai_response
                        )
                        saved_ai_message = chat_service.add_message(
                            target_session_id, user.id, ai_message
                        )

                        if saved_ai_message:
                            # Send AI response
                            ai_msg = WebSocketMessage(
                                type="chat_message",
                                content=ai_response,
                                session_id=target_session_id,
                                timestamp=saved_ai_message.created_at,
                            )
                            await manager.send_message_to_session(
                                ai_msg.json(), user.id, target_session_id
                            )

                elif message_type == "ping":
                    # Respond to ping with pong
                    pong_message = WebSocketMessage(
                        type="pong", content="pong", timestamp=datetime.utcnow()
                    )
                    await manager.send_personal_message(pong_message.json(), websocket)

                else:
                    # Invalid message format
                    error_message = WebSocketMessage(
                        type="error",
                        content="Invalid message format",
                        timestamp=datetime.utcnow(),
                    )
                    await manager.send_personal_message(error_message.json(), websocket)

            except json.JSONDecodeError:
                error_message = WebSocketMessage(
                    type="error",
                    content="Invalid JSON format",
                    timestamp=datetime.utcnow(),
                )
                await manager.send_personal_message(error_message.json(), websocket)

            except Exception as e:
                error_message = WebSocketMessage(
                    type="error",
                    content=f"Server error: {str(e)}",
                    timestamp=datetime.utcnow(),
                )
                await manager.send_personal_message(error_message.json(), websocket)

    except Exception as e:
        print(f"WebSocket error for user {user.id}: {e}")
    finally:
        await manager.disconnect(websocket, user.id, session_id)


async def generate_ai_response(
    user_message: str, conversation_history: list = None
) -> str:
    """
    Generate AI response to user message.
    This integrates with the AI service for better responses.
    """
    try:
        from app.services.ai_service import ai_service

        # Prepare conversation history if available
        messages = conversation_history or []

        # Generate response using AI service
        response = await ai_service.generate_response(messages, user_message)
        return response

    except Exception as e:
        print(f"AI service error: {e}")
        # Fallback to simple responses
        await asyncio.sleep(1)

        responses = [
            f"I understand you said: '{user_message}'. How can I help you further?",
            f"That's interesting! Regarding '{user_message}', let me think about that...",
            f"Thank you for sharing: '{user_message}'. What would you like to know?",
            "I'm here to help! Could you provide more details about what you're looking for?",
            "That's a great question! Let me provide you with some information on that topic.",
        ]

        import random

        return random.choice(responses)

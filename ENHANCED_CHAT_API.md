# Enhanced Multi-User Chat System API

This document describes the enhanced REST API for the chat system that supports multi-user functionality.

## Overview

The enhanced chat system now supports:

- **Multi-user chat sessions** with role-based permissions
- **Public/private/invite-only** session types
- **Session management** (create, update, delete by owners/admins)
- **Participant management** (join, leave, invite, remove)
- **Role-based permissions** (Owner, Admin, Member, Viewer)
- **Enhanced messaging** with user attribution

## Session Types

### SessionType Enum

- `PRIVATE`: Only the owner can access
- `PUBLIC`: Anyone can join freely
- `INVITE_ONLY`: Only invited users can join

### ParticipantRole Enum

- `OWNER`: User who created the session (full control)
- `ADMIN`: Can manage session and participants
- `MEMBER`: Can send messages
- `VIEWER`: Can only view messages (read-only)

## API Endpoints

### Authentication Required

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Chat Sessions

#### 1. Create Chat Session

**POST** `/api/v1/chat/sessions`

Creates a new chat session. The creator becomes the owner.

**Request Body:**

```json
{
  "title": "My Chat Room",
  "description": "A general discussion room",
  "session_type": "PUBLIC",
  "max_participants": 25
}
```

**Response:**

```json
{
  "id": 1,
  "title": "My Chat Room",
  "description": "A general discussion room",
  "session_type": "PUBLIC",
  "max_participants": 25,
  "user_id": 123,
  "owner_username": "john_doe",
  "is_active": true,
  "created_at": "2024-08-12T10:00:00Z",
  "updated_at": "2024-08-12T10:00:00Z",
  "participants": [
    {
      "id": 1,
      "user_id": 123,
      "username": "john_doe",
      "role": "OWNER",
      "joined_at": "2024-08-12T10:00:00Z",
      "is_active": true
    }
  ],
  "messages": [],
  "participant_count": 1
}
```

#### 2. Get User's Chat Sessions

**GET** `/api/v1/chat/sessions?skip=0&limit=100`

Gets all chat sessions where the user is a participant.

**Response:**

```json
[
  {
    "id": 1,
    "title": "My Chat Room",
    "description": "A general discussion room",
    "session_type": "PUBLIC",
    "owner_username": "john_doe",
    "created_at": "2024-08-12T10:00:00Z",
    "updated_at": "2024-08-12T10:00:00Z",
    "message_count": 5,
    "participant_count": 3
  }
]
```

#### 3. Get Public Sessions

**GET** `/api/v1/chat/sessions/public?skip=0&limit=100`

Gets public chat sessions that the user can join.

**Response:**

```json
{
  "sessions": [
    {
      "id": 2,
      "title": "Open Discussion",
      "description": "Public discussion room",
      "session_type": "PUBLIC",
      "owner_username": "jane_doe",
      "created_at": "2024-08-12T11:00:00Z",
      "updated_at": "2024-08-12T11:30:00Z",
      "message_count": 0,
      "participant_count": 1
    }
  ],
  "total": 1
}
```

#### 4. Get Specific Chat Session

**GET** `/api/v1/chat/sessions/{session_id}`

Gets a specific chat session with all details (participants and messages).

**Response:** Same format as Create Chat Session response.

#### 5. Update Chat Session

**PUT** `/api/v1/chat/sessions/{session_id}`

Updates a chat session (owner/admin only).

**Request Body:**

```json
{
  "title": "Updated Room Name",
  "description": "Updated description",
  "session_type": "INVITE_ONLY",
  "max_participants": 15
}
```

#### 6. Delete Chat Session

**DELETE** `/api/v1/chat/sessions/{session_id}`

Soft deletes a chat session (owner only).

**Response:** 204 No Content

### Participant Management

#### 7. Join Public Session

**POST** `/api/v1/chat/sessions/{session_id}/join`

Join a public chat session.

**Request Body:**

```json
{}
```

**Response:**

```json
{
  "message": "Successfully joined the chat session",
  "participant_id": 5
}
```

#### 8. Leave Session

**POST** `/api/v1/chat/sessions/{session_id}/leave`

Leave a chat session (owners cannot leave their own sessions).

**Response:**

```json
{
  "message": "Successfully left the chat session"
}
```

#### 9. Invite User to Session

**POST** `/api/v1/chat/sessions/{session_id}/invite`

Invite a user to a chat session (owner/admin only).

**Request Body:**

```json
{
  "user_id": 456,
  "role": "MEMBER"
}
```

**Response:**

```json
{
  "id": 6,
  "user_id": 456,
  "username": "alice_smith",
  "role": "MEMBER",
  "joined_at": "2024-08-12T12:00:00Z",
  "is_active": true
}
```

#### 10. Update Participant Role

**PUT** `/api/v1/chat/sessions/{session_id}/participants/{user_id}/role`

Update a participant's role (owner/admin only).

**Request Body:**

```json
{
  "role": "ADMIN"
}
```

#### 11. Remove Participant

**DELETE** `/api/v1/chat/sessions/{session_id}/participants/{user_id}`

Remove a participant from session (owner/admin only).

**Response:**

```json
{
  "message": "Participant removed successfully"
}
```

#### 12. Get Session Participants

**GET** `/api/v1/chat/sessions/{session_id}/participants`

Get all active participants in a chat session.

**Response:**

```json
[
  {
    "id": 1,
    "user_id": 123,
    "username": "john_doe",
    "role": "OWNER",
    "joined_at": "2024-08-12T10:00:00Z",
    "is_active": true
  },
  {
    "id": 2,
    "user_id": 456,
    "username": "alice_smith",
    "role": "MEMBER",
    "joined_at": "2024-08-12T11:15:00Z",
    "is_active": true
  }
]
```

### Messages

#### 13. Send Message

**POST** `/api/v1/chat/sessions/{session_id}/messages`

Send a message to a chat session (participants only, viewers cannot send).

**Request Body:**

```json
{
  "role": "user",
  "content": "Hello everyone!"
}
```

**Response:**

```json
{
  "id": 15,
  "session_id": 1,
  "user_id": 123,
  "username": "john_doe",
  "role": "user",
  "content": "Hello everyone!",
  "created_at": "2024-08-12T12:30:00Z"
}
```

#### 14. Get Session Messages

**GET** `/api/v1/chat/sessions/{session_id}/messages?skip=0&limit=100`

Get messages for a chat session (all participants can read).

**Response:**

```json
[
  {
    "id": 15,
    "session_id": 1,
    "user_id": 123,
    "username": "john_doe",
    "role": "user",
    "content": "Hello everyone!",
    "created_at": "2024-08-12T12:30:00Z"
  }
]
```

## Permission Matrix

| Action              | Owner | Admin | Member | Viewer |
| ------------------- | ----- | ----- | ------ | ------ |
| View messages       | ✅    | ✅    | ✅     | ✅     |
| Send messages       | ✅    | ✅    | ✅     | ❌     |
| Update session      | ✅    | ✅    | ❌     | ❌     |
| Delete session      | ✅    | ❌    | ❌     | ❌     |
| Invite users        | ✅    | ✅    | ❌     | ❌     |
| Remove participants | ✅    | ✅    | ❌     | ❌     |
| Change roles        | ✅    | ✅\*  | ❌     | ❌     |
| Leave session       | ❌    | ✅    | ✅     | ✅     |

\*Admins can change roles but cannot make someone an owner or change the owner's role.

## Error Responses

Standard HTTP status codes are used:

- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

Error response format:

```json
{
  "detail": "Error description"
}
```

## Rate Limiting

API endpoints may be rate-limited. Check response headers for rate limit information.

## WebSocket Support

Real-time messaging is supported via WebSocket connections. See WebSocket documentation for details on connecting and receiving real-time updates.

## Examples

### Complete Flow: Create Public Room and Have Users Join

1. **User A creates a public room:**

```bash
curl -X POST "http://localhost:8000/api/v1/chat/sessions" \
  -H "Authorization: Bearer <token_a>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "General Discussion",
    "description": "Open chat for everyone",
    "session_type": "PUBLIC",
    "max_participants": 50
  }'
```

2. **User B joins the public room:**

```bash
curl -X POST "http://localhost:8000/api/v1/chat/sessions/1/join" \
  -H "Authorization: Bearer <token_b>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

3. **User B sends a message:**

```bash
curl -X POST "http://localhost:8000/api/v1/chat/sessions/1/messages" \
  -H "Authorization: Bearer <token_b>" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "content": "Hi everyone! Just joined."
  }'
```

4. **User A promotes User B to admin:**

```bash
curl -X PUT "http://localhost:8000/api/v1/chat/sessions/1/participants/456/role" \
  -H "Authorization: Bearer <token_a>" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "ADMIN"
  }'
```

This enhanced API provides comprehensive functionality for managing multi-user chat sessions with proper permissions and role-based access control.

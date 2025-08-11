"""Add multi-user chat functionality

Revision ID: 002
Revises: 001
Create Date: 2024-08-12 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types with checkfirst
    session_type_enum = postgresql.ENUM(
        "PRIVATE", "PUBLIC", "INVITE_ONLY", name="sessiontype", create_type=False
    )
    session_type_enum.create(op.get_bind(), checkfirst=True)

    participant_role_enum = postgresql.ENUM(
        "OWNER", "ADMIN", "MEMBER", "VIEWER", name="participantrole", create_type=False
    )
    participant_role_enum.create(op.get_bind(), checkfirst=True)

    # Add new columns to chat_sessions
    op.add_column("chat_sessions", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "chat_sessions",
        sa.Column(
            "session_type", session_type_enum, nullable=False, server_default="PRIVATE"
        ),
    )
    op.add_column(
        "chat_sessions",
        sa.Column(
            "max_participants", sa.Integer(), nullable=False, server_default="10"
        ),
    )

    # Add user_id to chat_messages
    op.add_column("chat_messages", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_chat_messages_user_id", "chat_messages", "users", ["user_id"], ["id"]
    )

    # Create chat_participants table
    op.create_table(
        "chat_participants",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "role", participant_role_enum, nullable=False, server_default="MEMBER"
        ),
        sa.Column(
            "joined_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("session_id", "user_id", name="unique_session_user"),
    )

    # Create indexes for better performance
    op.create_index(
        "idx_chat_participants_session_id", "chat_participants", ["session_id"]
    )
    op.create_index("idx_chat_participants_user_id", "chat_participants", ["user_id"])
    op.create_index("idx_chat_participants_active", "chat_participants", ["is_active"])
    op.create_index("idx_chat_sessions_type", "chat_sessions", ["session_type"])
    op.create_index("idx_chat_messages_user_id", "chat_messages", ["user_id"])


def downgrade():
    # Drop indexes
    op.drop_index("idx_chat_messages_user_id")
    op.drop_index("idx_chat_sessions_type")
    op.drop_index("idx_chat_participants_active")
    op.drop_index("idx_chat_participants_user_id")
    op.drop_index("idx_chat_participants_session_id")

    # Drop chat_participants table
    op.drop_table("chat_participants")

    # Remove foreign key and column from chat_messages
    op.drop_constraint("fk_chat_messages_user_id", "chat_messages", type_="foreignkey")
    op.drop_column("chat_messages", "user_id")

    # Remove columns from chat_sessions
    op.drop_column("chat_sessions", "max_participants")
    op.drop_column("chat_sessions", "session_type")
    op.drop_column("chat_sessions", "description")

    # Drop enums
    sa.Enum(name="sessiontype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="participantrole").drop(op.get_bind(), checkfirst=True)

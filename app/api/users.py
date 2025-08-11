from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.dependencies import get_current_active_user
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile."""
    user_service = UserService(db)

    # Check if email is being changed and if it's already taken
    if user_update.email and user_update.email != current_user.email:
        if user_service.is_email_taken(
            user_update.email, exclude_user_id=current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Check if username is being changed and if it's already taken
    if user_update.username and user_update.username != current_user.username:
        if user_service.is_username_taken(
            user_update.username, exclude_user_id=current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

    updated_user = user_service.update_user(current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_current_user(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Deactivate current user account."""
    user_service = UserService(db)
    success = user_service.deactivate_user(current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return None

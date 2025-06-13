from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any # For current_user type hint flexibility

from ....app import schemas # Adjusted import path
from ....app import crud # Adjusted import path
from ....app import models # Adjusted import path
from ....app.database import get_db # Adjusted import path
from ....app.auth import get_current_active_user # Adjusted import path

router = APIRouter()

@router.post("/profile", response_model=schemas.user.User, status_code=status.HTTP_201_CREATED)
def create_or_update_user_profile(
    user_in: schemas.user.UserCreate,
    db: Session = Depends(get_db)
) -> models.user.User:
    """
    Create a new user profile or update an existing one based on Google ID.
    For this initial version, we'll focus on creation.
    The `google_id` and `email` are expected in `user_in` (UserCreate schema).
    """
    # Check if user already exists by google_id or email to prevent duplicates
    # For simplicity, this example prioritizes google_id for lookup.
    db_user_by_google_id = crud.crud_user.get_user_by_google_id(db, google_id=user_in.google_id)
    if db_user_by_google_id:
        # User exists, could update here if UserUpdate schema and CRUD were implemented
        # For now, let's raise an error if trying to create an existing user by google_id
        # Or, we could return the existing user. Let's return existing for now.
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this Google ID already exists")
        return db_user_by_google_id

    db_user_by_email = crud.crud_user.get_user_by_email(db, email=user_in.email)
    if db_user_by_email:
        # User exists with this email but different google_id (should ideally not happen with Google OAuth)
        # Or, this email is already taken.
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        return db_user_by_email

    # If no existing user, create new user
    created_user = crud.crud_user.create_user(db=db, user=user_in)
    return created_user

@router.get("/profile", response_model=schemas.user.User)
def read_user_profile(
    db: Session = Depends(get_db),
    # The `get_current_active_user` stub returns a dict: {"username": "fakeuser", "email": "fakeuser@example.com", ...}
    # We need to simulate fetching a user based on this.
    # For a real app, `get_current_active_user` would return a `models.user.User` instance
    # or at least enough info (like google_id) to fetch it.
    current_user_stub: Any = Depends(get_current_active_user)
) -> models.user.User:
    """
    Get current user's profile.
    This endpoint is protected; `get_current_active_user` simulates authentication.
    The current stub for `get_current_active_user` doesn't provide a real google_id from a token.
    So, for now, this will be a conceptual endpoint.
    Let's try to fetch a user based on the stub's email if possible, or a default user.
    """
    # In a real scenario, current_user_stub would be a models.User object
    # or would contain an identifier (e.g., google_id) from the decoded token.

    # Attempt to use email from stub, assuming it's unique and tied to a user
    # This is a temporary workaround due to the auth stub limitations.
    user_email = current_user_stub.get("email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials or extract user identifier from token stub"
        )

    db_user = crud.crud_user.get_user_by_email(db, email=user_email)

    if db_user is None:
        # This case means the authenticated user (from stub) doesn't exist in DB.
        # This could happen if the stub email is not in sync with any created user.
        # Or, if we want to enforce that a profile must be created first via POST.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found for authenticated user.")

    return db_user

# Example of a protected endpoint using the current_user object
# @router.get("/profile/me/items")
# async def read_own_items(current_user: models.user.User = Depends(get_current_active_user)):
# # This would work if get_current_active_user returned a User model instance
# return [{"item_id": "Foo", "owner": current_user.email}]

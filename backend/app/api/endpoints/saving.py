from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....app import crud, models, schemas # Adjusted import path
from ....app.database import get_db # Adjusted import path
from ....app.auth import get_current_active_user # Adjusted import path

router = APIRouter()

@router.post("/", response_model=schemas.saving.Saving, status_code=status.HTTP_201_CREATED)
def create_saving_for_current_user(
    saving_in: schemas.saving.SavingCreate,
    db: Session = Depends(get_db),
    current_user_stub: Any = Depends(get_current_active_user)
) -> models.saving.Saving:
    """
    Create a new saving entry for the currently authenticated user.
    User ID is derived from the auth stub via email (temporary workaround).
    """
    user_email = current_user_stub.get("email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials or extract user identifier from token stub"
        )

    db_user = crud.crud_user.get_user_by_email(db, email=user_email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user not found in database."
        )

    return crud.crud_saving.create_user_saving(db=db, saving=saving_in, user_id=db_user.id)

@router.get("/", response_model=List[schemas.saving.Saving])
def read_savings_for_current_user(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user_stub: Any = Depends(get_current_active_user)
) -> List[models.saving.Saving]:
    """
    Retrieve savings for the currently authenticated user.
    User ID is derived from the auth stub via email (temporary workaround).
    """
    user_email = current_user_stub.get("email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials or extract user identifier from token stub"
        )

    db_user = crud.crud_user.get_user_by_email(db, email=user_email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user not found in database."
        )

    savings = crud.crud_saving.get_savings_by_user(db, user_id=db_user.id, skip=skip, limit=limit)
    return savings

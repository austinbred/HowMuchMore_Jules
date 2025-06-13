from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....app import crud, models, schemas # Adjusted import path
from ....app.database import get_db # Adjusted import path
from ....app.auth import get_current_active_user # Adjusted import path

router = APIRouter()

@router.get("/", response_model=schemas.assumption.Assumption)
def read_user_assumptions(
    db: Session = Depends(get_db),
    current_user_stub: Any = Depends(get_current_active_user)
) -> Any: # Return type can be models.assumption.Assumption or schemas.assumption.AssumptionBase
    """
    Retrieve the assumptions for the currently authenticated user.
    If no assumptions are stored for the user, return default values.
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

    db_assumption = crud.crud_assumption.get_assumption_by_user(db, user_id=db_user.id)

    if not db_assumption:
        # Per revised plan, raise 404. Frontend can use AssumptionCreate schema for defaults.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assumptions not found for this user. Please create them first."
        )

    return db_assumption

@router.post("/", response_model=schemas.assumption.Assumption, status_code=status.HTTP_200_OK) # 200 if updating, 201 if creating
def create_or_update_user_assumptions_endpoint(
    assumption_in: schemas.assumption.AssumptionCreate, # AssumptionCreate has defaults for all fields
    db: Session = Depends(get_db),
    current_user_stub: Any = Depends(get_current_active_user)
) -> models.assumption.Assumption:
    """
    Create or update assumptions for the currently authenticated user.
    Uses AssumptionCreate schema which provides defaults if not supplied by client.
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

    # The CRUD function handles both creation and update
    return crud.crud_assumption.create_or_update_user_assumption(
        db=db,
        assumption_in=assumption_in,
        user_id=db_user.id
    )

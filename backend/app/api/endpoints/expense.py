from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....app import crud, models, schemas # Adjusted import path
from ....app.database import get_db # Adjusted import path
from ....app.auth import get_current_active_user # Adjusted import path

router = APIRouter()

@router.post("/", response_model=schemas.expense.Expense, status_code=status.HTTP_201_CREATED)
def create_expense_for_current_user(
    expense_in: schemas.expense.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user_stub: Any = Depends(get_current_active_user) # Using Any for the stub
) -> models.expense.Expense:
    """
    Create a new expense for the currently authenticated user.
    The current_user_stub is a placeholder. In a real app, it would provide user ID.
    For now, we need a way to get a user_id. Let's assume the stub's email
    can be used to fetch the user_id, similar to the GET /profile endpoint.
    Or, if `get_current_active_user` could be modified to return a user model directly, that'd be better.
    Let's proceed assuming we can get the user from the stub's email.
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

    return crud.crud_expense.create_user_expense(db=db, expense=expense_in, user_id=db_user.id)

@router.get("/", response_model=List[schemas.expense.Expense])
def read_expenses_for_current_user(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user_stub: Any = Depends(get_current_active_user) # Using Any for the stub
) -> List[models.expense.Expense]:
    """
    Retrieve expenses for the currently authenticated user.
    Similar to POST, we derive user_id from the stub.
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

    expenses = crud.crud_expense.get_expenses_by_user(db, user_id=db_user.id, skip=skip, limit=limit)
    return expenses

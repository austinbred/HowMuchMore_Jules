from typing import List, Optional
from sqlalchemy.orm import Session

from .. import models # Access models like models.expense.Expense
from .. import schemas # Access schemas like schemas.expense.ExpenseCreate

def create_user_expense(db: Session, expense: schemas.expense.ExpenseCreate, user_id: int) -> models.expense.Expense:
    """
    Create a new expense entry for a specific user.
    """
    db_expense = models.expense.Expense(
        **expense.dict(),  # Unpack ExpenseCreate schema
        user_id=user_id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.expense.Expense]:
    """
    Retrieve all expenses for a specific user, with pagination.
    """
    return db.query(models.expense.Expense)                 .filter(models.expense.Expense.user_id == user_id)                 .offset(skip)                 .limit(limit)                 .all()

# Optional placeholders for future CRUD operations:
# def get_expense(db: Session, expense_id: int, user_id: int) -> Optional[models.expense.Expense]:
#     """Get a specific expense by its ID and user_id to ensure ownership."""
#     return db.query(models.expense.Expense)    #              .filter(models.expense.Expense.id == expense_id, models.expense.Expense.user_id == user_id)    #              .first()

# def update_expense(db: Session, expense_id: int, expense_in: schemas.expense.ExpenseUpdate, user_id: int) -> Optional[models.expense.Expense]:
#     """Update an existing expense. Ensure user owns the expense."""
#     db_expense = get_expense(db, expense_id=expense_id, user_id=user_id)
#     if db_expense:
#         update_data = expense_in.dict(exclude_unset=True)
#         for key, value in update_data.items():
#             setattr(db_expense, key, value)
#         db.commit()
#         db.refresh(db_expense)
#     return db_expense

# def delete_expense(db: Session, expense_id: int, user_id: int) -> Optional[models.expense.Expense]:
#     """Delete an expense. Ensure user owns the expense."""
#     db_expense = get_expense(db, expense_id=expense_id, user_id=user_id)
#     if db_expense:
#         db.delete(db_expense)
#         db.commit()
#     return db_expense

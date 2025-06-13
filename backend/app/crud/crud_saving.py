from typing import List, Optional
from sqlalchemy.orm import Session

from .. import models # Access models like models.saving.Saving
from .. import schemas # Access schemas like schemas.saving.SavingCreate

def create_user_saving(db: Session, saving: schemas.saving.SavingCreate, user_id: int) -> models.saving.Saving:
    """
    Create a new saving entry for a specific user.
    """
    db_saving = models.saving.Saving(
        **saving.dict(),  # Unpack SavingCreate schema
        user_id=user_id
    )
    db.add(db_saving)
    db.commit()
    db.refresh(db_saving)
    return db_saving

def get_savings_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.saving.Saving]:
    """
    Retrieve all savings for a specific user, with pagination.
    """
    return db.query(models.saving.Saving)                 .filter(models.saving.Saving.user_id == user_id)                 .offset(skip)                 .limit(limit)                 .all()

# Optional placeholders for future CRUD operations:
# def get_saving(db: Session, saving_id: int, user_id: int) -> Optional[models.saving.Saving]:
#     """Get a specific saving by its ID and user_id to ensure ownership."""
#     return db.query(models.saving.Saving)    #              .filter(models.saving.Saving.id == saving_id, models.saving.Saving.user_id == user_id)    #              .first()

# def update_saving(db: Session, saving_id: int, saving_in: schemas.saving.SavingUpdate, user_id: int) -> Optional[models.saving.Saving]:
#     """Update an existing saving. Ensure user owns the saving."""
#     # Similar logic to update_expense
#     pass

# def delete_saving(db: Session, saving_id: int, user_id: int) -> Optional[models.saving.Saving]:
#     """Delete a saving. Ensure user owns the saving."""
#     # Similar logic to delete_expense
#     pass

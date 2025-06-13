from typing import Optional
from sqlalchemy.orm import Session

from .. import models # To access models.assumption.Assumption
from .. import schemas # To access schemas.assumption.AssumptionCreate/Update

def get_assumption_by_user(db: Session, user_id: int) -> Optional[models.assumption.Assumption]:
    """
    Retrieve the assumption settings for a specific user.
    Since it's a one-to-one relationship, there should be at most one.
    """
    return db.query(models.assumption.Assumption)                 .filter(models.assumption.Assumption.user_id == user_id)                 .first()

def create_or_update_user_assumption(
    db: Session,
    assumption_in: schemas.assumption.AssumptionCreate, # Or AssumptionUpdate if fields are optional
    user_id: int
) -> models.assumption.Assumption:
    """
    Create new assumption settings for a user if they don't exist,
    or update existing ones.
    The schema AssumptionCreate has defaults, so all fields will be present.
    If using AssumptionUpdate, we would need to handle partial updates carefully.
    For now, let's assume assumption_in contains all fields (as per AssumptionCreate).
    """
    db_assumption = get_assumption_by_user(db, user_id=user_id)

    if db_assumption:
        # Update existing assumptions
        # Using .dict() ensures we only try to update fields present in the schema
        update_data = assumption_in.dict()
        for key, value in update_data.items():
            setattr(db_assumption, key, value)
    else:
        # Create new assumptions
        db_assumption = models.assumption.Assumption(
            **assumption_in.dict(),
            user_id=user_id
        )
        db.add(db_assumption)

    db.commit()
    db.refresh(db_assumption)
    return db_assumption

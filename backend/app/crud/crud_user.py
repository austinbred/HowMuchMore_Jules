from typing import Optional
from sqlalchemy.orm import Session

from .. import models # Assuming models is accessible like this
from .. import schemas # Assuming schemas is accessible like this

def get_user(db: Session, user_id: int) -> Optional[models.user.User]:
    return db.query(models.user.User).filter(models.user.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.user.User]:
    return db.query(models.user.User).filter(models.user.User.email == email).first()

def get_user_by_google_id(db: Session, google_id: str) -> Optional[models.user.User]:
    return db.query(models.user.User).filter(models.user.User.google_id == google_id).first()

def create_user(db: Session, user: schemas.user.UserCreate) -> models.user.User:
    """
    Creates a new user in the database.
    'google_id' is expected to be part of the user schema (UserCreate).
    """
    db_user = models.user.User(
        email=user.email,
        google_id=user.google_id, # Directly from the schema
        age=user.age,
        start_year=user.start_year
        # is_active is True by default in the model
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Placeholder for update_user, if needed later for the POST /profile endpoint
# def update_user(db: Session, user_id: int, user_update: schemas.user.UserUpdate) -> Optional[models.user.User]:
#     db_user = get_user(db, user_id)
#     if db_user:
#         update_data = user_update.dict(exclude_unset=True)
#         for key, value in update_data.items():
#             setattr(db_user, key, value)
#         db.commit()
#         db.refresh(db_user)
#     return db_user

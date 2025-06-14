from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    google_id: str
    age: int # Changed to required
    start_year: Optional[int] = None

class UserCreate(UserBase):
    # Password is not handled here for Google OAuth
    pass

class User(UserBase):
    id: int
    # google_id is inherited from UserBase and is now mandatory
    is_active: bool = True # is_active can remain, or be True by default

    class Config:
        orm_mode = True # Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, but an ORM model

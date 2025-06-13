from pydantic import BaseModel
from typing import Optional, Literal

class SavingBase(BaseModel):
    name: str
    amount: float
    frequency: Literal["monthly", "quarterly", "yearly"] # Or perhaps just 'current_total', 'monthly_contribution'

class SavingCreate(SavingBase):
    pass

class Saving(SavingBase):
    id: int
    user_id: int # Foreign key to User

    class Config:
        orm_mode = True

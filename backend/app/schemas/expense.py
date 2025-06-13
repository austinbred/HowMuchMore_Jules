from pydantic import BaseModel
from typing import Optional, Literal

class ExpenseBase(BaseModel):
    name: str
    amount: float
    frequency: Literal["monthly", "quarterly", "yearly"]

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    user_id: int # Foreign key to User

    class Config:
        orm_mode = True

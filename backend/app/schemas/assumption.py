from pydantic import BaseModel
from typing import Optional

class AssumptionBase(BaseModel):
    return_rate: float = 0.07 # Default 7%
    inflation_rate: float = 0.02 # Default 2%
    life_expectancy: int = 95 # Default 95 years

class AssumptionCreate(AssumptionBase):
    pass

class Assumption(AssumptionBase):
    id: int
    user_id: int # Foreign key to User

    class Config:
        orm_mode = True

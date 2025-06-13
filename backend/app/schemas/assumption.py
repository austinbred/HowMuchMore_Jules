from pydantic import BaseModel, Field # Field can be used for more detailed validation if needed
from typing import Optional

class AssumptionBase(BaseModel):
    # Defaults are defined here as per the issue spec and previous setup
    return_rate: float = Field(default=0.07, gt=0, description="Annual rate of return on investments (e.g., 0.07 for 7%)")
    inflation_rate: float = Field(default=0.02, ge=0, description="Annual inflation rate (e.g., 0.02 for 2%)")
    life_expectancy: int = Field(default=95, gt=0, description="Expected life expectancy in years (e.g., 95)")

class AssumptionCreate(AssumptionBase):
    # This schema is used when creating/updating assumptions.
    # It inherits all fields and defaults from AssumptionBase.
    pass

class AssumptionUpdate(BaseModel):
    # This schema is used for partial updates. All fields are optional.
    return_rate: Optional[float] = Field(default=None, gt=0, description="Annual rate of return on investments (e.g., 0.07 for 7%)")
    inflation_rate: Optional[float] = Field(default=None, ge=0, description="Annual inflation rate (e.g., 0.02 for 2%)")
    life_expectancy: Optional[int] = Field(default=None, gt=0, description="Expected life expectancy in years (e.g., 95)")

class Assumption(AssumptionBase):
    # This is the schema for responses (data returned from API).
    id: int
    # user_id: int # Not including user_id as these will be fetched via /user/assumptions for the authenticated user.

    class Config:
        orm_mode = True # Enables the model to be populated from ORM objects

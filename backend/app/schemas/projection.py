from pydantic import BaseModel
from typing import List, Optional

class ProjectionResult(BaseModel):
    lifestyle: str  # e.g., "frugal", "content", "luxury"
    retirement_age: Optional[int]
    can_retire: bool # True if retirement_age is not None, False otherwise

    # Optional: Add a constructor or validator to set can_retire based on retirement_age
    # from pydantic import root_validator
    # @root_validator(pre=False, skip_on_failure=True) # Using pre=False to run after other validators
    # def set_can_retire(cls, values):
    #     values["can_retire"] = values.get("retirement_age") is not None
    #     return values
    # For simplicity, we can set this directly when creating the object in the endpoint.

class ProjectionResponse(BaseModel):
    projections: List[ProjectionResult]

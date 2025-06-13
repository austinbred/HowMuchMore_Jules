# This file makes the 'schemas' directory a Python package.
from .user import User, UserCreate # Assuming these are the primary ones exported
from .expense import Expense, ExpenseCreate
from .saving import Saving, SavingCreate
from .assumption import Assumption, AssumptionCreate, AssumptionUpdate, AssumptionBase
from .projection import ProjectionResult, ProjectionResponse # Add this

# Optional: Define __all__
# __all__ = [
#     "User", "UserCreate",
#     "Expense", "ExpenseCreate",
#     "Saving", "SavingCreate",
#     "Assumption", "AssumptionCreate", "AssumptionUpdate", "AssumptionBase",
#     "ProjectionResult", "ProjectionResponse"
# ]

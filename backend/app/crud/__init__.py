# This file makes the 'crud' directory a Python package.
from .crud_user import get_user, get_user_by_email, get_user_by_google_id, create_user
from .crud_expense import create_user_expense, get_expenses_by_user
from .crud_saving import create_user_saving, get_savings_by_user
from .crud_assumption import get_assumption_by_user, create_or_update_user_assumption # Add this

# Optional: Define __all__
# __all__ = [
#     "get_user", "get_user_by_email", "get_user_by_google_id", "create_user",
#     "create_user_expense", "get_expenses_by_user",
#     "create_user_saving", "get_savings_by_user",
#     "get_assumption_by_user", "create_or_update_user_assumption"
# ]

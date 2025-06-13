# This file makes the 'models' directory a Python package.
from .user import User
from .expense import Expense
from .saving import Saving
from .assumption import Assumption # Add this line

# Optional: Define __all__ to control what `from .models import *` imports
# __all__ = ["User", "Expense", "Saving", "Assumption"]

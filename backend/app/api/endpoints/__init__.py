# This file makes the 'endpoints' directory a Python package.
from .user import router as user_router
from .expense import router as expense_router
from .saving import router as saving_router
from .assumption import router as assumption_router
from .projection import router as projection_router # Add this

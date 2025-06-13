from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship # Ensure this is imported
from ..database import Base
# If Expense model is in a separate file and User needs to know about it for type hinting (optional but good practice)
# from .expense import Expense # This might cause circular import if not handled carefully, usually relationship string name is enough

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=False) # Changed to nullable=False
    email = Column(String, unique=True, index=True, nullable=False)

    age = Column(Integer, nullable=True)
    start_year = Column(Integer, nullable=True) # The year they start using the app / planning

    is_active = Column(Boolean, default=True)

    # Add or update the expenses relationship
    expenses = relationship("Expense", back_populates="owner", cascade="all, delete-orphan")

    # Add the savings relationship
    savings = relationship("Saving", back_populates="owner", cascade="all, delete-orphan")

    # assumptions relationship will be added later
    # assumptions = relationship("Assumption", back_populates="owner", uselist=False) # Assuming one set of assumptions per user

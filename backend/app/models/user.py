from sqlalchemy import Column, Integer, String, Boolean # Removed Float as it's not used
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=False) # Changed to nullable=False
    email = Column(String, unique=True, index=True, nullable=False)

    age = Column(Integer, nullable=True)
    start_year = Column(Integer, nullable=True) # The year they start using the app / planning

    is_active = Column(Boolean, default=True)

    # Relationships (placeholders for now, will be defined later)
    # expenses = relationship("Expense", back_populates="owner")
    # savings = relationship("Saving", back_populates="owner")
    # assumptions = relationship("Assumption", back_populates="owner", uselist=False) # Assuming one set of assumptions per user

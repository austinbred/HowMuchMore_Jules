from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base

class Assumption(Base):
    __tablename__ = "assumptions"

    id = Column(Integer, primary_key=True, index=True)
    # Default values in the model can be set using `default=` argument in Column
    # However, Pydantic schemas are often a better place for business logic defaults.
    # For the model, we'll define the type and nullability.
    # Defaults from the issue (7%, 2%, 95) will be handled by Pydantic schemas primarily.
    return_rate = Column(Float, nullable=False, default=0.07)
    inflation_rate = Column(Float, nullable=False, default=0.02)
    life_expectancy = Column(Integer, nullable=False, default=95)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    owner = relationship("User", back_populates="assumption") # Singular: assumption

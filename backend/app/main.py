from fastapi import FastAPI

# Import for table creation
from .database import engine, Base # Assuming Base is the declarative_base() instance

# Assuming the router object in user.py is named 'router'
from .api.endpoints import user as user_api

# Function to create database tables
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="Financial Retirement Planner API")

# Event handler for startup
app.add_event_handler("startup", create_db_and_tables)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Financial Retirement Planner API"}

# Include the user router
app.include_router(user_api.router, prefix="/user", tags=["user"])

# Placeholder for future routers for other features
# from .api import expenses, savings, assumptions, projections # noqa
# app.include_router(expenses.router, prefix="/user", tags=["expenses"]) # noqa
# app.include_router(savings.router, prefix="/user", tags=["savings"]) # noqa
# app.include_router(assumptions.router, prefix="/user", tags=["assumptions"]) # noqa
# app.include_router(projections.router, prefix="/user", tags=["projections"]) # noqa

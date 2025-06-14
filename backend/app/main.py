from fastapi import FastAPI

# Import for table creation
from .database import engine, Base

# Import routers from the endpoints package using their exported names

from .api.endpoints import ( # Using parentheses for multi-line import
    user_router,
    expense_router,
    saving_router,
    assumption_router,
    projection_router # Added projection_router
)

# Function to create database tables
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="Financial Retirement Planner API")

# Event handler for startup
app.add_event_handler("startup", create_db_and_tables)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Financial Retirement Planner API"}

# Include the routers
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(expense_router, prefix="/user/expenses", tags=["expenses"])
app.include_router(saving_router, prefix="/user/savings", tags=["savings"])
app.include_router(assumption_router, prefix="/user/assumptions", tags=["assumptions"])
app.include_router(projection_router, prefix="/user/projections", tags=["projections"]) # Added projection_router


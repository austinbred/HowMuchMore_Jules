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

app = FastAPI(title="Financial Retirement Planner API")


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Financial Retirement Planner API"}



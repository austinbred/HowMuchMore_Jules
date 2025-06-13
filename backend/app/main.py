from fastapi import FastAPI

app = FastAPI(title="Financial Retirement Planner API")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Financial Retirement Planner API"}

# Placeholder for future routers
# from .api import users, expenses, savings, assumptions, projections # noqa
# app.include_router(users.router, prefix="/user", tags=["user"]) # noqa
# app.include_router(expenses.router, prefix="/user", tags=["expenses"]) # noqa
# app.include_router(savings.router, prefix="/user", tags=["savings"]) # noqa
# app.include_router(assumptions.router, prefix="/user", tags=["assumptions"]) # noqa
# app.include_router(projections.router, prefix="/user", tags=["projections"]) # noqa

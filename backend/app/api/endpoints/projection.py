from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....app import crud, models, schemas # Main app's modules
from ....app.database import get_db
from ....app.auth import get_current_active_user
from ....app.core.projections import ( # Core projection logic
    LIFESTYLE_MULTIPLIERS,
    calculate_retirement_projection,
    get_total_annual_amount
)

router = APIRouter()

# Name for the specific saving item that holds the current total lump sum
# This is based on the assumption in the plan to avoid immediate Saving model changes.
LUMP_SUM_SAVING_NAME = "Current Total Savings"

@router.get("/", response_model=schemas.projection.ProjectionResponse)
def get_retirement_projections(
    db: Session = Depends(get_db),
    current_user_stub: Any = Depends(get_current_active_user)
) -> schemas.projection.ProjectionResponse:
    """
    Calculate and return retirement projections for different lifestyles.
    """
    user_email = current_user_stub.get("email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials or extract user identifier from token stub"
        )

    db_user = crud.crud_user.get_user_by_email(db, email=user_email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user not found in database."
        )

    if db_user.age is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # Or 422 Unprocessable Entity
            detail="User age is not set. Please update user profile."
        )
    current_age = db_user.age

    # Fetch assumptions or use defaults
    user_assumptions = crud.crud_assumption.get_assumption_by_user(db, user_id=db_user.id)
    if user_assumptions:
        investment_return_rate = user_assumptions.return_rate
        inflation_rate = user_assumptions.inflation_rate
        life_expectancy = user_assumptions.life_expectancy
    else:
        # Use defaults from Pydantic schema if no DB entry
        default_assumptions = schemas.assumption.AssumptionBase()
        investment_return_rate = default_assumptions.return_rate
        inflation_rate = default_assumptions.inflation_rate
        life_expectancy = default_assumptions.life_expectancy

    # Calculate base annual expenses
    user_expenses = crud.crud_expense.get_expenses_by_user(db, user_id=db_user.id, limit=1000) # High limit
    base_annual_expenses = get_total_annual_amount(user_expenses)

    # Derive current_savings_total and annual_savings_contribution
    user_savings = crud.crud_saving.get_savings_by_user(db, user_id=db_user.id, limit=1000) # High limit
    current_savings_total: float = 0.0
    recurring_savings_items: List[models.saving.Saving] = []

    for saving_item in user_savings:
        if saving_item.name == LUMP_SUM_SAVING_NAME:
             # Assuming frequency for lump sum is 'one-time' or its amount is taken as is.
             # If it has a frequency like 'yearly', it might be misinterpreted by get_total_annual_amount.
             # For now, just sum up amounts of items with this specific name.
            current_savings_total += saving_item.amount
        else:
            # Add to list for annual contribution calculation, if not 'one-time' frequency
            if saving_item.frequency != "one-time": # Make sure 'one-time' is handled by normalize
                 recurring_savings_items.append(saving_item)

    annual_savings_contribution = get_total_annual_amount(recurring_savings_items)

    # --- Debug prints (remove in production) ---
    # print(f"User Age: {current_age}")
    # print(f"Investment Rate: {investment_return_rate}, Inflation: {inflation_rate}, Life Expectancy: {life_expectancy}")
    # print(f"Base Annual Expenses: {base_annual_expenses}")
    # print(f"Current Total Savings: {current_savings_total}")
    # print(f"Annual Savings Contribution: {annual_savings_contribution}")
    # --- End Debug prints ---

    projection_results: List[schemas.projection.ProjectionResult] = []

    for lifestyle, multiplier in LIFESTYLE_MULTIPLIERS.items():
        # print(f"Calculating for lifestyle: {lifestyle}, multiplier: {multiplier}")
        retirement_age = calculate_retirement_projection(
            current_age=current_age,
            current_savings_total=current_savings_total,
            annual_savings_contribution=annual_savings_contribution,
            base_annual_expenses=base_annual_expenses, # This is already the total for user
            investment_return_rate=investment_return_rate,
            inflation_rate=inflation_rate,
            life_expectancy=life_expectancy,
            expense_multiplier=multiplier
        )
        # print(f"Lifestyle: {lifestyle}, Calculated Age: {retirement_age}")

        projection_results.append(
            schemas.projection.ProjectionResult(
                lifestyle=lifestyle,
                retirement_age=retirement_age,
                can_retire=(retirement_age is not None)
            )
        )

    return schemas.projection.ProjectionResponse(projections=projection_results)

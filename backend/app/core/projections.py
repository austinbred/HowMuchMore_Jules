from typing import List, Union, Literal, Optional, Dict # Ensure Optional and Dict are imported
# It's better to import the specific models if they are type-hinted in function signatures
# to avoid potential circular dependencies if models also import from core.
# For now, we'll use string forward references or import them if direct usage is needed.
# from ..models.expense import Expense # Example if type hinting needs concrete type
# from ..models.saving import Saving # Example if type hinting needs concrete type

# Forward declaration for type hints if models are not directly imported
# This is often needed if models.py might import from core.py too.
# However, for List[Union[Expense, Saving]], we'd typically import the actual classes.
# Let's assume direct imports are fine for now, as core.projections is unlikely
# to be imported by the model files themselves.
from ..models.expense import Expense
from ..models.saving import Saving


VALID_FREQUENCIES = Literal["monthly", "quarterly", "yearly", "one-time"] # Added "one-time"

def normalize_item_to_annual(amount: float, frequency: VALID_FREQUENCIES) -> float:
    """
    Normalizes a single financial item's amount to an annual value based on its frequency.
    Items with frequency 'one-time' are considered as already annualized or not contributing to annual flow.
    For this function, 'one-time' will return 0 as it's not an ongoing annual amount.
    This might need adjustment based on how 'one-time' items are treated in broader logic
    (e.g. distinguishing one-time savings for current total vs. one-time expenses).
    """
    if frequency == "monthly":
        return amount * 12
    elif frequency == "quarterly":
        return amount * 4
    elif frequency == "yearly":
        return amount
    elif frequency == "one-time":
        return 0 # Or amount, depending on interpretation. For annual *flow*, it's 0.
    else:
        # This case should ideally not be reached if frequency is validated by Pydantic Literal
        raise ValueError(f"Invalid frequency: {frequency}. Expected one of {VALID_FREQUENCIES}.")

def get_total_annual_amount(items: List[Union[Expense, Saving]]) -> float:
    """
    Calculates the total annual amount from a list of Expense or Saving items.
    It skips items that are designated as 'one-time' frequency for calculating annual flow.
    This function is for recurring annual expenses or contributions.
    """
    total_annual = 0.0
    for item in items:
        # We need to ensure 'frequency' is a valid attribute and matches VALID_FREQUENCIES
        # The Pydantic models for Expense and Saving should enforce this.
        # For 'one-time' items, normalize_item_to_annual will return 0, effectively skipping them
        # from the sum of *annual recurring* amounts.
        if hasattr(item, 'frequency') and hasattr(item, 'amount'):
             # Ensure frequency is one of the expected literals.
             # Pydantic should handle this, but a runtime check or broader Literal type hint for item.frequency might be good.
            item_frequency = getattr(item, 'frequency')
            if item_frequency in get_args(VALID_FREQUENCIES): # Check if frequency is valid
                total_annual += normalize_item_to_annual(item.amount, item_frequency)
            # else: # Optional: handle or log unexpected frequency strings if they bypass Pydantic
                # print(f"Warning: Item {getattr(item, 'name', 'N/A')} has unexpected frequency '{item_frequency}'")
    return total_annual

# Helper to get arguments from Literal type, for runtime check if needed.
from typing import get_args


# Lifestyle multipliers
LIFESTYLE_MULTIPLIERS: Dict[str, float] = {
    "frugal": 1.0,
    "content": 1.5,
    "luxury": 2.5,
}

MAX_PROJECTION_YEARS = 100 # To prevent infinite loops in edge cases, e.g. never able to retire

def calculate_retirement_projection(
    current_age: int,
    current_savings_total: float,
    annual_savings_contribution: float, # Assumed to be in today's dollars, will be inflation-adjusted
    base_annual_expenses: float,      # In today's dollars
    investment_return_rate: float,    # Annual rate, e.g., 0.07
    inflation_rate: float,            # Annual rate, e.g., 0.02
    life_expectancy: int,
    expense_multiplier: float         # e.g., 1.0 for frugal, 1.5 for content
) -> Optional[int]:
    """
    Calculates the earliest age at which retirement is possible.

    Args:
        current_age: The current age of the individual.
        current_savings_total: Total current accumulated savings.
        annual_savings_contribution: Annual amount saved (in today's value, will inflate).
        base_annual_expenses: Current annual expenses (in today's value).
        investment_return_rate: Expected annual return on investments.
        inflation_rate: Expected annual inflation rate.
        life_expectancy: Age until which retirement funds must last.
        expense_multiplier: Factor applied to base_annual_expenses for desired retirement lifestyle.

    Returns:
        The calculated retirement age, or None if retirement is not possible
        within the projection window or by life expectancy.
    """

    if current_age >= life_expectancy:
        return None # Already past life expectancy

    # Initialize variables for the simulation loop
    age = current_age
    accumulated_savings = current_savings_total

    # These are nominal values that will inflate each year
    inflating_annual_contribution = annual_savings_contribution
    desired_annual_retirement_expenses_today = base_annual_expenses * expense_multiplier

    for year in range(MAX_PROJECTION_YEARS): # Loop year by year from current_age
        age = current_age + year

        if age >= life_expectancy: # Cannot retire if already at or past life expectancy within loop
            return None

        # Calculate expenses and savings contribution for the current age (year)
        # These are the values at the *beginning* of the year `age`.
        current_year_desired_expenses = desired_annual_retirement_expenses_today * ((1 + inflation_rate) ** year)
        current_year_contribution = inflating_annual_contribution * ((1 + inflation_rate) ** year)

        # Check if retirement is possible at the current 'age'
        # This involves simulating drawdown from 'age' to 'life_expectancy'

        # --- Start of drawdown simulation for retiring at current 'age' ---
        savings_at_retirement_candidate_age = accumulated_savings
        possible_to_retire_this_year = True
        temp_retirement_savings = savings_at_retirement_candidate_age

        for retirement_year_offset in range(life_expectancy - age + 1):
            # Expenses for this specific year of retirement
            # The 'year' variable tracks offset from current_age for overall projection.
            # 'retirement_year_offset' tracks years *into* retirement.
            # Expenses at (age + retirement_year_offset)
            # = desired_annual_retirement_expenses_today * (1+inflation_rate)^(year + retirement_year_offset)
            expenses_in_given_retirement_year = desired_annual_retirement_expenses_today * ((1 + inflation_rate) ** (year + retirement_year_offset))

            if temp_retirement_savings < expenses_in_given_retirement_year:
                possible_to_retire_this_year = False
                break # Not enough savings for this year of retirement

            temp_retirement_savings -= expenses_in_given_retirement_year
            temp_retirement_savings *= (1 + investment_return_rate) # Remaining savings grow

        if possible_to_retire_this_year:
            return age # Found the earliest retirement age
        # --- End of drawdown simulation ---

        # If not retiring this year, accrue savings for the next year:
        # Savings grow by investment return
        accumulated_savings *= (1 + investment_return_rate)
        # Add this year's contribution (which has also grown with inflation)
        accumulated_savings += current_year_contribution

        if accumulated_savings < 0 and investment_return_rate < 0: # Avoid negative infinity due to high negative returns
             if accumulated_savings < -1_000_000_000: # Arbitrary large negative number
                 return None


    return None # Retirement not possible within MAX_PROJECTION_YEARS

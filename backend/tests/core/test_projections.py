import pytest
from typing import List, Union, NamedTuple # For mock items

# Assuming the module to test is accessible like this:
# This might require PYTHONPATH adjustments or running pytest from 'backend' directory
from ....app.core.projections import (
    normalize_item_to_annual,
    get_total_annual_amount,
    calculate_retirement_projection,
    LIFESTYLE_MULTIPLIERS # If needed for test setup
)
# If the above import fails, a simpler relative import might work if structure allows:
# from ...app.core.projections import ...

# Mock structure for Expense/Saving items for get_total_annual_amount tests
class MockFinancialItem(NamedTuple):
    name: str
    amount: float
    frequency: str # Should match VALID_FREQUENCIES Literal

# --- Tests for normalize_item_to_annual ---
@pytest.mark.parametrize("amount, frequency, expected", [
    (100.0, "monthly", 1200.0),
    (100.0, "quarterly", 400.0),
    (100.0, "yearly", 100.0),
    (100.0, "one-time", 0.0), # As per current logic for annual flow
    (0.0, "monthly", 0.0),
])
def test_normalize_item_to_annual(amount, frequency, expected):
    assert normalize_item_to_annual(amount, frequency) == expected

def test_normalize_item_to_annual_invalid_frequency():
    with pytest.raises(ValueError): # Or TypeError depending on Literal enforcement
        normalize_item_to_annual(100.0, "bi-weekly") # type: ignore

# --- Tests for get_total_annual_amount ---
def test_get_total_annual_amount_empty_list():
    assert get_total_annual_amount([]) == 0.0

def test_get_total_annual_amount_mixed_items():
    items: List[MockFinancialItem] = [
        MockFinancialItem(name="Salary", amount=5000, frequency="monthly"), # 60000
        MockFinancialItem(name="Bonus", amount=10000, frequency="yearly"),   # 10000
        MockFinancialItem(name="Freelance", amount=1000, frequency="quarterly"),# 4000
        MockFinancialItem(name="Gift", amount=500, frequency="one-time"),    # 0
    ]
    # Expected: 60000 + 10000 + 4000 + 0 = 74000
    assert get_total_annual_amount(items) == 74000.0 # type: ignore

def test_get_total_annual_amount_with_invalid_frequency_item():
    # Test robustness if an item with invalid frequency somehow gets passed
    # The function currently skips items with frequencies not in VALID_FREQUENCIES Literal set
    items = [
        MockFinancialItem(name="Valid", amount=100, frequency="yearly"),
        MockFinancialItem(name="InvalidFreq", amount=1000, frequency="unknown")
    ]
    assert get_total_annual_amount(items) == 100.0 # type: ignore
    # This test depends on the runtime check `if item_frequency in get_args(VALID_FREQUENCIES):`
    # in get_total_annual_amount

# --- Tests for calculate_retirement_projection ---
# Basic success case
def test_calc_ret_proj_success():
    age = calculate_retirement_projection(
        current_age=30,
        current_savings_total=100000,
        annual_savings_contribution=10000, # Inflates
        base_annual_expenses=40000,        # Inflates
        investment_return_rate=0.07,
        inflation_rate=0.02,
        life_expectancy=95,
        expense_multiplier=1.0 # Frugal
    )
    assert age is not None
    assert 30 < age < 95 # Expect retirement age to be reasonable

# Not possible to retire case (e.g., very high expenses or low savings)
def test_calc_ret_proj_not_possible_high_expenses():
    age = calculate_retirement_projection(
        current_age=30,
        current_savings_total=10000,
        annual_savings_contribution=1000,
        base_annual_expenses=100000, # Very high expenses
        investment_return_rate=0.05,
        inflation_rate=0.02,
        life_expectancy=95,
        expense_multiplier=1.0
    )
    assert age is None

# Edge case: Already past life expectancy (should return None immediately)
def test_calc_ret_proj_already_past_life_expectancy():
    age = calculate_retirement_projection(
        current_age=96,
        current_savings_total=1000000,
        annual_savings_contribution=10000,
        base_annual_expenses=40000,
        investment_return_rate=0.07,
        inflation_rate=0.02,
        life_expectancy=95,
        expense_multiplier=1.0
    )
    assert age is None

# Edge case: Retiring immediately or very soon
def test_calc_ret_proj_retire_immediately():
    # Sufficient savings to cover all future expenses from day 1
    age = calculate_retirement_projection(
        current_age=60,
        current_savings_total=3000000, # High savings
        annual_savings_contribution=0,
        base_annual_expenses=50000,
        investment_return_rate=0.03, # Low return to make it challenging but possible
        inflation_rate=0.01,
        life_expectancy=90,
        expense_multiplier=1.0
    )
    # If logic is correct, and savings are truly sufficient for all years of retirement
    # from current_age, it should return current_age.
    assert age == 60

def test_calc_ret_proj_zero_inflation_zero_return():
    # Test with no inflation and no investment return (savings only grow by contribution)
    # Should still be able to retire if contributions are high enough relative to expenses
    # This tests if the growth calculations handle zeros correctly.
    age = calculate_retirement_projection(
        current_age=30,
        current_savings_total=0,
        annual_savings_contribution=25000, # Saving 25k/yr
        base_annual_expenses=25000,       # Spending 25k/yr
        investment_return_rate=0.00,
        inflation_rate=0.00,
        life_expectancy=60, # Needs to last 30 years (30*25k = 750k)
        expense_multiplier=1.0
    )
    # With 0 return, 0 inflation:
    # Year 0 (age 30): savings 0, expenses 25k. Needs 25k * 30 = 750k.
    # Year 1 (age 30): adds 25k. total 25k.
    # ... needs 750k / 25k = 30 years of saving. So should retire at 30+30 = 60.
    # However, the simulation checks if one can retire *at the current age*.
    # So at age 30, savings=0, cannot retire.
    # At age 59, savings = 29*25k = 725k. Expenses = 25k. Needs 25k * (60-59) = 25k. Can retire.
    # The loop will continue until retirement is possible.
    # The check is `if possible_to_retire_this_year: return age`
    # The drawdown simulation for age 59:
    #   savings_at_retirement_candidate_age = 29 * 25000 = 725000
    #   retirement_year_offset = 0 (retiring at 59, for age 59 expenses)
    #     expenses_in_given_retirement_year = 25000
    #     temp_retirement_savings = 725000 - 25000 = 700000
    #   retirement_year_offset = 1 (retiring at 59, for age 60 expenses)
    #     expenses_in_given_retirement_year = 25000
    #     temp_retirement_savings = 700000 - 25000 = 675000
    # This will pass. So it should return 59.
    assert age == 59

# Add more specific scenarios if needed, e.g., different multipliers
def test_calc_ret_proj_content_lifestyle():
    age = calculate_retirement_projection(
        current_age=30,
        current_savings_total=100000,
        annual_savings_contribution=15000, # Higher contribution
        base_annual_expenses=40000,
        investment_return_rate=0.07,
        inflation_rate=0.02,
        life_expectancy=95,
        expense_multiplier=LIFESTYLE_MULTIPLIERS["content"] # 1.5x expenses
    )
    assert age is not None
    # Expect retirement age to be later than frugal or may not be possible
    # For this test, just ensure it runs and returns an age or None
    if age is not None:
        assert 30 < age < 95

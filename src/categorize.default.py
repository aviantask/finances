import re
from typing import Optional
from src.model import Category
from src.overrides import OverrideManager

# Regex rules map: Pattern -> Category
# Order matters: first match wins
RULES = [
    # --- Income ---
    (r"(?i)Salary", Category.SALARY),
    (r"(?i)Interest Credit", Category.OTHER_INCOME),

    # --- Housing ---
    (r"(?i)Rent", Category.RENT),

    # --- Tax ---
    (r"(?i)tax", Category.TAX),

    # --- Kids ---
    (r"(?i)Preschool Fees", Category.SCHOOL),
    (r"(?i)Piano", Category.KIDS),

    # --- Living: Groceries & Household ---
    (r"(?i)Woolworths", Category.GROCERIES),
    (r"(?i)Coles", Category.GROCERIES),
    (r"(?i)Aldi", Category.GROCERIES),
    (r"(?i)Bunnings", Category.GROCERIES),
    (r"(?i)Chemist", Category.GROCERIES),
    (r"(?i)Pharmacy", Category.GROCERIES),
    (r"(?i)Post Office", Category.GROCERIES),
    (r"(?i)IKEA", Category.GROCERIES),
    (r"(?i)Kmart", Category.GROCERIES),
    (r"(?i)Target", Category.GROCERIES),
    (r"(?i)Big W", Category.GROCERIES),
    (r"(?i)Officeworks", Category.GROCERIES),

    # --- Living: Eating Out ---
    (r"(?i)McDonalds", Category.EATING_OUT),
    (r"(?i)KFC", Category.EATING_OUT),
    (r"(?i)Uber.*Eats", Category.EATING_OUT),
    (r"(?i)Doordash", Category.EATING_OUT),

    # --- Living: Transport ---
    (r"(?i)Trainlink", Category.TRANSPORT),
    (r"(?i)Fuel", Category.TRANSPORT),
    (r"(?i)Petrol", Category.TRANSPORT),

    # --- Living: Utilities ---
    (r"(?i)Energy", Category.UTILITIES),
    (r"(?i)Water", Category.UTILITIES),
    (r"(?i)Telstra", Category.UTILITIES),

    # --- Living: Health ---
    (r"(?i)Gym", Category.HEALTH),
    (r"(?i)Pharma", Category.HEALTH),
    (r"(?i)Medical", Category.HEALTH),
    (r"(?i)Optical", Category.HEALTH),
    (r"(?i)Dental", Category.HEALTH),
    (r"(?i)Dentist", Category.HEALTH),

    # --- Misc ---
    (r"(?i)Amazon", Category.MISC), # Fallback for Amazon shopping
    (r"(?i)PayPal", Category.MISC),

    # --- System / Transfers ---
    (r"(?i)Internal Transfer", Category.INTERNAL_TRANSFER),
    (r"(?i)Transfer to", Category.INTERNAL_TRANSFER),
]

def categorize_transaction(description: str, txn_id: str, overrides: Optional[OverrideManager] = None) -> str:
    """
    Categorizes a transaction.
    1. Checks overrides (by ID).
    2. Checks regex rules (by Description).
    3. Returns MISC.
    """
    # 1. Check Overrides
    if overrides:
        forced_cat = overrides.get_override(txn_id)
        if forced_cat:
            return forced_cat

    # 2. Check Regex Rules
    for pattern, category in RULES:
        if re.search(pattern, description):
            return category.value
            
    # 3. Fallback
    return Category.MISC.value

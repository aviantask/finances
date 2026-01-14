from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Category(str, Enum):
    # Income
    SALARY = "Salary"
    OTHER_INCOME = "Other Income"
    
    # Housing
    RENT = "Rent"
    
    # Living
    GROCERIES = "Groceries & Household"
    EATING_OUT = "Eating Out"
    TRANSPORT = "Transport"
    UTILITIES = "Utilities & Services"
    HEALTH = "Health & Fitness"
    
    # Kids
    SCHOOL = "School"
    KIDS = "Kids"
    
    # Tax
    TAX = "Tax"
    
    # Misc
    MISC = "Misc. Spending"
    
    # System
    INTERNAL_TRANSFER = "Internal Transfer"
    
    # Manual
    ONE_OFF = "One-Off Expenses"

@dataclass(frozen=True)
class Transaction:
    id: str
    date: str
    account: str
    description: str
    amount: float
    category: Optional[str] = None
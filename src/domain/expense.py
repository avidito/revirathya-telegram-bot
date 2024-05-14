from datetime import date
from typing import Optional, Protocol
from pydantic import BaseModel

from src.domain.types import TypeFormatter


# Entity
class FactExpense(BaseModel):
    """Fact Expense: Transaction of Expense data"""
    id: Optional[int] = None
    budget_type_id: int
    date: date
    description: str
    amount: int

    class Config:
        json_encoders = {
            date: TypeFormatter.convert_date_to_ymd
        }


# Repository
class ExpenseRepositoryAPI(Protocol):
    """
    Expense - Repository API

    Repository for handling data fetch from Finance API for Expense data.
    """
    
    def create(self, expense: FactExpense) -> FactExpense:
        """
        Create - Expense

        Send expense data to be created on Finance service via API.

        :params
            expense: FactExpense. New expense data.
        
        :return
            FactExpense. Newly created expense data.
        """
        pass


# Usecase
class ExpenseUsecase(Protocol):
    """
    Expense - Usecase

    Usecase for handling process around Expense.
    """

    async def create(self, expense: FactExpense) -> FactExpense:
        """
        Create - Expense

        Create (or record) new Expense data.

        :params
            expense: FactExpense. New expense data.
        
        :return
            FactExpense. Newly created expense data.
        """
        pass

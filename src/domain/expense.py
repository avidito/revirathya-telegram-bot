from datetime import date
from typing import Optional, Protocol
from pydantic import BaseModel

from src.domain.types import TypeFormatter


# Entity
class FactExpense(BaseModel):
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
class ExpenseAPIRepository(Protocol):
    def create(self, expense: FactExpense) -> FactExpense:
        pass


# Usecase
class ExpenseUsecase(Protocol):
    async def create(self, expense: FactExpense) -> FactExpense:
        pass

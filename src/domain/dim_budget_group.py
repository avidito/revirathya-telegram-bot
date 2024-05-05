from typing import List, Protocol
from pydantic import BaseModel


# Entity
class DimBudgetGroup(BaseModel):
    id: int
    budget_group: str
    callback_value: str


# Repository
class DimBudgetGroupAPIRepository(Protocol):
    def fetch(self) -> List[DimBudgetGroup]:
        pass


# Usecase
class DimBudgetGroupUsecase(Protocol):
    def fetch(self) -> List[DimBudgetGroup]:
        pass

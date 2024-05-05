from typing import List, Protocol
from pydantic import BaseModel


# Entity
class DimBudgetGroup(BaseModel):
    id: int
    budget_group: str

class DimBudgetType(BaseModel):
    id: int
    budget_group_id: int
    budget_type: str


# Repository
class BudgetRepository(Protocol):
    def get_groups(self) -> List[DimBudgetGroup]:
        pass

    def get_types_by_group(self, budget_group_id: int) -> List[DimBudgetType]:
        pass


# Usecase
class BudgetUsecase(Protocol):
    async def get_groups(self) -> List[DimBudgetGroup]:
        pass

    async def get_types_by_group(self, budget_group_id: int) -> List[DimBudgetType]:
        pass

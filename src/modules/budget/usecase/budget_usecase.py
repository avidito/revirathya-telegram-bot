from typing import List

from src.domain.budget import (
    DimBudgetGroup,
    DimBudgetType,
    BudgetRepository,
)


class BudgetUsecaseImpl:
    __repo: BudgetRepository

    def __init__(self, repo: BudgetRepository):
        self.__repo = repo
    

    async def get_groups(self) -> List[DimBudgetGroup]:
        dim_budget_group_list = self.__repo.get_groups()
        return dim_budget_group_list
    
    async def get_types_by_group(self, budget_group_id: int) -> List[DimBudgetType]:
        dim_budget_type_list = self.__repo.get_types_by_group(budget_group_id)
        return dim_budget_type_list

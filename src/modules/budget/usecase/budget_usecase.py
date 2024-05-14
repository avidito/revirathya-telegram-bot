from typing import List

from src.domain.budget import (
    DimBudgetGroup,
    DimBudgetType,
    BudgetRepositoryAPI,
)


class BudgetUsecaseImpl:
    """Budget - Usecase Implementation"""
    __repo_api: BudgetRepositoryAPI

    def __init__(self, repo_api: BudgetRepositoryAPI):
        self.__repo_api = repo_api
    

    async def get_groups(self) -> List[DimBudgetGroup]:
        dim_budget_group_list = self.__repo_api.get_groups()
        return dim_budget_group_list
    
    async def get_types_by_group(self, budget_group_id: int) -> List[DimBudgetType]:
        dim_budget_type_list = self.__repo_api.get_types_by_group(budget_group_id)
        return dim_budget_type_list

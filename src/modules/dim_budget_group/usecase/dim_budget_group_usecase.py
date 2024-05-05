from typing import List

from src.domain.dim_budget_group import (
    DimBudgetGroup,
    DimBudgetGroupAPIRepository,
)


class DimBudgetGroupUsecaseImpl:
    __api_repo: DimBudgetGroupAPIRepository

    def __init__(self, api_repo: DimBudgetGroupAPIRepository):
        self.__api_repo = api_repo
    

    async def fetch(self) -> List[DimBudgetGroup]:
        dim_budget_group_list = self.__api_repo.fetch()
        return dim_budget_group_list

import requests
from typing import List, Optional

from src.domain.budget import (
    DimBudgetGroup,
    DimBudgetType,
)


class BudgetRepositoryImpl:
    __url: str

    def __init__(self, host: str, port: Optional[int], protocol: str = "http"):
        self.__url = f"{protocol}://{host}:{port}" if (port) else f"{protocol}://{host}"
    

    def get_groups(self) -> List[DimBudgetGroup]:
        # Get Data
        url = "/".join([self.__url, "dim-budget-groups"])
        req = requests.get(url)

        # Parse Response
        responses = req.json()
        dim_budget_group_list = [
            DimBudgetGroup(**row)
            for row in responses
        ]
        return dim_budget_group_list
    

    def get_types_by_group(self, budget_group_id: int) -> List[DimBudgetType]:
        # Get Data
        url = "/".join([self.__url, "dim-budget-groups", str(budget_group_id), "types"])
        req = requests.get(url)

        # Parse Response
        responses = req.json()
        dim_budget_group_list = [
            DimBudgetType(**row)
            for row in responses
        ]
        return dim_budget_group_list


import requests
from typing import List, Optional

from src.domain.dim_budget_group import (
    DimBudgetGroup,
)


class DimBudgetGroupAPIRepositoryImpl:
    __url: str

    def __init__(self, host: str, route: str, port: Optional[int], protocol: str = "http"):
        self.__url = f"{protocol}://{host}:{port}/{route}" if (port) else f"{protocol}://{host}/{route}"
    

    def fetch(self) -> List[DimBudgetGroup]:
        req = requests.get(self.__url)
        responses = req.json()

        dim_budget_group_list = [
            DimBudgetGroup(**row)
            for row in responses
        ]
        return dim_budget_group_list


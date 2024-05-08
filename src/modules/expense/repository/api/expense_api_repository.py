import requests
from typing import List, Optional

from src.domain.expense import FactExpense


class ExpenseAPIRepositoryImpl:
    __url: str

    def __init__(self, host: str, port: Optional[int], protocol: str = "http"):
        self.__url = f"{protocol}://{host}:{port}" if (port) else f"{protocol}://{host}"
    

    def create(self, expense: FactExpense) -> FactExpense:
        # Insert Data
        url = "/".join([self.__url, "fact-expenses"])
        req = requests.post(
            url,
            json = expense.model_dump(
                exclude = {"id",},
                mode = "json",
            )
        )

        try:
            req.raise_for_status()
        except Exception:
            raise Exception(expense.model_dump(exclude=("id",), mode="json"))

        # Parse Response
        response = req.json()
        fact_expense = FactExpense(**response)
        
        return fact_expense

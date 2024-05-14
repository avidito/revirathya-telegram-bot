from src.domain.expense import (
    FactExpense,
    ExpenseRepositoryAPI,
)


class ExpenseUsecaseImpl:
    """Expense - Usecase Implementation"""
    __repo_api: ExpenseRepositoryAPI

    def __init__(self, repo_api: ExpenseRepositoryAPI):
        self.__repo_api = repo_api
    

    async def create(self, expense: FactExpense) -> FactExpense:
        fact_expense = self.__repo_api.create(expense)
        return fact_expense

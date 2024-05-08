from src.domain.expense import (
    FactExpense,
    ExpenseAPIRepository,
)


class ExpenseUsecaseImpl:
    __repo: ExpenseAPIRepository

    def __init__(self, repo: ExpenseAPIRepository):
        self.__repo = repo
    

    async def create(self, expense: FactExpense) -> FactExpense:
        fact_expense = self.__repo.create(expense)
        return fact_expense

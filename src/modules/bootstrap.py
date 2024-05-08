from src.helpers.config import Config
from src.domain import (
    budget,
    expense,
)

from src.modules.budget import BudgetRepositoryImpl, BudgetUsecaseImpl
from src.modules.expense import ExpenseAPIRepositoryImpl, ExpenseUsecaseImpl


# Repository
class RepositoryAPI:
    budget_repo: budget.BudgetRepository
    expense_db_repo: expense.ExpenseAPIRepository

    def __init__(self, C: Config):
        self.budget_repo = BudgetRepositoryImpl(host=C.FIN_API_HOSTNAME, port=C.FIN_API_PORT)
        self.expense_api_repo = ExpenseAPIRepositoryImpl(host=C.FIN_API_HOSTNAME, port=C.FIN_API_PORT)


# Usecase
class Usecase:
    budget_usecase: budget.BudgetUsecase
    expense_usecase: expense.ExpenseUsecase

    def __init__(self, repo_api: RepositoryAPI):
        self.budget_usecase = BudgetUsecaseImpl(repo_api.budget_repo)
        self.expense_usecase = ExpenseUsecaseImpl(repo_api.expense_api_repo)


# Bootstrap
def bootstrap_modules(C: Config):
    repo_api = RepositoryAPI(C)
    usecase = Usecase(repo_api)
    return usecase

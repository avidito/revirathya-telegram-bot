from src.helpers.config import Config
from src.domain import (
    budget,
    expense,
)

from src.modules.budget import BudgetRepositoryAPIImpl, BudgetUsecaseImpl
from src.modules.expense import ExpenseAPIRepositoryImpl, ExpenseUsecaseImpl


# Repository
class RepositoryAPI:
    """
    Collection of Repository for interacting with API.

    :params
        C [Config]: Config from environment variables.
    """
    budget_repo: budget.BudgetRepositoryAPI
    expense_db_repo: expense.ExpenseRepositoryAPI

    def __init__(self, C: Config):
        self.budget_repo = BudgetRepositoryAPIImpl(host=C.FIN_API_HOSTNAME, port=C.FIN_API_PORT)
        self.expense_api_repo = ExpenseAPIRepositoryImpl(host=C.FIN_API_HOSTNAME, port=C.FIN_API_PORT)


# Usecase
class Usecase:
    """
    Collection of Usecase for handling business process.

    :params
        RepositoryAPI: Collection of Repository for interacting with API.
    """
    budget_usecase: budget.BudgetUsecase
    expense_usecase: expense.ExpenseUsecase

    def __init__(self, repo_api: RepositoryAPI):
        self.budget_usecase = BudgetUsecaseImpl(repo_api.budget_repo)
        self.expense_usecase = ExpenseUsecaseImpl(repo_api.expense_api_repo)


# Bootstrap
def bootstrap_modules(C: Config):
    """
    Bootstraping Modules

    Initialize Usecase by generate all the necessary repository for registered usecase.

    :params
        C [Config]: Config from environment variables.
    
    :return
        Usecase. Collection of Usecase for handling business process.
    """
    repo_api = RepositoryAPI(C)
    usecase = Usecase(repo_api)
    return usecase

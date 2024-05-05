from src.helpers.config import Config
from src.domain.budget import (
    BudgetRepository,
    BudgetUsecase,
)
from src.modules.budget import BudgetRepositoryImpl, BudgetUsecaseImpl


# Repository
class Repository:
    budget_repo: BudgetRepository

    def __init__(self, C: Config):
        self.budget_repo = BudgetRepositoryImpl(host=C.FIN_API_HOSTNAME, port=C.FIN_API_PORT)


# Usecase
class Usecase:
    budget_usecase: BudgetUsecase

    def __init__(self, r: Repository):
        self.budget_usecase = BudgetUsecaseImpl(r.budget_repo)


# Bootstrap
def bootstrap_modules(C: Config):
    repository = Repository(C)
    usecase = Usecase(repository)
    return usecase

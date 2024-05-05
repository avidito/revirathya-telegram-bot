from typing import Optional

from src.helpers.config import Config
from src.domain.dim_budget_group import (
    DimBudgetGroupAPIRepository,
    DimBudgetGroupUsecase,
)
from src.modules.dim_budget_group import DimBudgetGroupAPIRepositoryImpl, DimBudgetGroupUsecaseImpl


# Repository
class Repository:
    dim_budget_group_api_repo: DimBudgetGroupAPIRepository

    def __init__(self, C: Config):
        self.dim_budget_group_api_repo = DimBudgetGroupAPIRepositoryImpl(host=C.FIN_API_HOSTNAME, port=C.FIN_API_PORT, route="dim-budget-groups")


# Usecase
class Usecase:
    dim_budget_group_usecase: DimBudgetGroupUsecase

    def __init__(self, r: Repository):
        self.dim_budget_group_usecase = DimBudgetGroupUsecaseImpl(r.dim_budget_group_api_repo)


# Bootstrap
def bootstrap_modules(C: Config):
    repository = Repository(C)
    usecase = Usecase(repository)
    return usecase

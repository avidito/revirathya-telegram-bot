from typing import List, Protocol
from pydantic import BaseModel


# Entity
class DimBudgetGroup(BaseModel):
    """Dim Budget Group: Dimension data of Budget Grouping"""
    id: int
    budget_group: str

class DimBudgetType(BaseModel):
    """Dim Budget Type: Dimension data of Budget Type/Category"""
    id: int
    budget_group_id: int
    budget_type: str


# Repository
class BudgetRepositoryAPI(Protocol):
    """
    Budget - Repository API

    Repository for handling data fetch from Finance API for Budget Group and Types data.
    """

    def get_groups(self) -> List[DimBudgetGroup]:
        """
        Get Groups - Budget

        Get list of all Budget Groups via API.

        :params
            None
        
        :return
            list[DimBudgetGroup]. List of Budget Group data.
        """
        pass


    def get_types_by_group(self, budget_group_id: int) -> List[DimBudgetType]:
        """
        Get Types by Group - Budget

        Get list of all Budget Type based on selected Budget Group via API.

        :params
            budget_group_id [int]: Budget Group ID for requested list of Budget Types.
        
        :return
            list[DimBudgetType]. List of Budget Type data.
        """
        pass


# Usecase
class BudgetUsecase(Protocol):
    """
    Budget - Usecase

    Usecase for handling process around Budget Group and Types.
    """

    async def get_groups(self) -> List[DimBudgetGroup]:
        """
        Get Groups - Budget

        Get list of all Budget Groups.

        :params
            None
        
        :return
            list[DimBudgetGroup]. List of Budget Group data.
        """
        pass


    async def get_types_by_group(self, budget_group_id: int) -> List[DimBudgetType]:
        """
        Get Types by Group - Budget

        Get list of all Budget Type based on selected Budget Group.

        :params
            budget_group_id [int]: Budget Group ID for requested list of Budget Types.
        
        :return
            list[DimBudgetType]. List of Budget Type data.
        """
        pass

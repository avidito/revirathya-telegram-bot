from typing import Optional
from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    date: Optional[str] = Field(default=None)
    budget_group: Optional[str] = Field(default=None)
    budget_type: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    amount: Optional[int] = Field(default=None)


    # Methods
    def get_budget_group_id(self) -> int:
        return int(self.budget_group.split(";")[0])
    
    def get_budget_type_id(self) -> int:
        return int(self.budget_type.split(";")[0])
    
    def to_message(self) -> str:
        _budget_group = self.budget_group.split(";")[1] if (self.budget_group) else None
        _budget_type = self.budget_type.split(";")[1] if (self.budget_type) else None

        message = "\n".join(
            row for row in
            [
                f"<b>Date</b>: {self.date}" if (self.date) else None,
                f"<b>Budget Group</b>: {_budget_group}" if (_budget_group) else None,
                f"<b>Budget Type</b>: {_budget_type}" if (_budget_type) else None,
                f"<b>Description</b>: {self.description}" if (self.description) else None,
                f"<b>Amount</b>: Rp {int(self.amount):_},00".replace("_", ".") if (self.amount) else None,
            ]
            if row is not None
        )
        return message
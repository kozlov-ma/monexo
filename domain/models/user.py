from __future__ import annotations

import typing
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class User:
    id: int

    days_left: int

    remaining_budget: float = 0
    budget_today: float = 0

    expense_today: float = 0
    income_today: float = 0

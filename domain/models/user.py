from dataclasses import dataclass
from uuid import UUID
from datetime import date


@dataclass
class User:
    id: UUID
    telegram_id: str
    period: date
    budget: int
    expense: int
    income: int

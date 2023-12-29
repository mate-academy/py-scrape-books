from dataclasses import dataclass
from typing import Literal


@dataclass
class BookItem:
    title: str
    price: float
    amount_in_stock: int
    rating: Literal["One", "Two", "Three", "Four", "Five"]
    category: str
    description: str
    upc: str
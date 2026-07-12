from dataclasses import dataclass
from typing import Optional


@dataclass
class ScrapeBooksItem:
    title: str
    price: float
    amount_in_stock: Optional[int]
    rating: int
    category: str
    description: str
    upc: str

import decimal
from dataclasses import dataclass


@dataclass
class BookScraperItem:
    title: str
    price: decimal
    amount_in_stock: int
    rating: str
    category: str
    description: str
    upc: str

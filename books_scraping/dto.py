from dataclasses import dataclass


@dataclass
class BookItem:
    title: str
    price: float
    amount_in_stock: int
    rating: int
    category: str
    description: str
    upc: str

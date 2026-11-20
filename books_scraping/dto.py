from dataclasses import dataclass


@dataclass
class BookDTO:
    title: str
    price: float
    amount_in_stock: int
    rating: int
    category: str
    description: str
    upc: str

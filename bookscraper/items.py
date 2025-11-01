from typing import TypedDict


class BookItem(TypedDict):
    title: str
    price: float
    amount_in_stock: int
    rating: int
    category: str
    description: str
    upc: str

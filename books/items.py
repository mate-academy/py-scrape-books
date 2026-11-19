from dataclasses import dataclass


@dataclass
class BooksItem:
    title: str | None = None
    price: float | None = None
    amount_in_stock: int | None = None
    rating: int | None = None
    category: str | None = None
    description: str | None = None
    upc: str | None = None

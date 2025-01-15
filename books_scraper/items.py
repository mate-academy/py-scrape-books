from dataclasses import dataclass


@dataclass
class BookItem:
    """Dataclass representing a book item."""
    title: str = None
    price: float = None
    amount_in_stock: int = None
    rating: int = None
    category: str = None
    description: str = None
    upc: str = None

from dataclasses import dataclass
from typing import Optional

@dataclass
class EcommerceItem:
    title: Optional[str] = None
    price: float = 0.0
    amount_in_stock: int = 0
    rating: int = 0
    category: Optional[str] = None
    description: Optional[str] = None
    upc: Optional[str] = None

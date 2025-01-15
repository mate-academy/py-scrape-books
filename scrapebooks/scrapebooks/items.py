# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class BookItem:
    title: str
    price: Decimal
    amount_in_stock: int
    rating: int
    category: str
    description: str
    upc: str

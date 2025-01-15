# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass


@dataclass
class BookItem:
    title: str = None
    price: float = None
    amount_in_stock: int = None
    rating: int = None
    category: str = None
    description: str = None
    upc: str = None

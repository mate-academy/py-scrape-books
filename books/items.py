# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass


@dataclass
class BooksItem:
    title: str | None = None
    price: float | None = None
    amount_in_stock: int = 0
    rating: int | None = None
    category: str | None = None
    description: str | None = None
    upc: str | None = None

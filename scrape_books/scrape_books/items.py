# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass


@dataclass
class ScrapeBooksItem:
    title: str |None
    price: str | None
    amount_in_stock: int | None
    rating: str | None
    description: str |None
    category: str | None
    upc: str | None


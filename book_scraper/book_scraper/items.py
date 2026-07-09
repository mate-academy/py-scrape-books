# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass


@dataclass
class BookScraperItem:
    title: str
    price: str
    amount_in_stock: int
    rating: int
    category: str
    description: str
    upc: str

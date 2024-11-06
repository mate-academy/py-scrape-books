# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from dataclasses import dataclass


@dataclass
class BooksToScrapeItem(scrapy.Item):
    title: str
    price: float
    amount_in_stock: int
    rating: int
    category: str
    description: str
    upc: str

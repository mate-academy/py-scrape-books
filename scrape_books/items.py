# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass


# class ScrapeBooksItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass

@dataclass
class BookItem:
    title: str
    price: float
    rating: int
    amount_in_stock: int = 0
    description: str = ""
    upc: str = ""

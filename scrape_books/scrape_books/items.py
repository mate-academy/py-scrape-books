# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from typing import Optional

import scrapy


class ScrapeBooksItem(scrapy.Item):
    title: Optional[str] = scrapy.Field()
    price: Optional[float] = scrapy.Field()
    amount_in_stock: Optional[int] = scrapy.Field()
    rating: Optional[str] = scrapy.Field()
    category: Optional[str] = scrapy.Field()
    description: Optional[str] = scrapy.Field()
    upc: Optional[str] = scrapy.Field()

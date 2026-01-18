# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksScrapingItem(scrapy.Item):
    title: str = scrapy.Field()
    price: float = scrapy.Field()
    amount_in_stock: int = scrapy.Field()
    rating: int = scrapy.Field()
    category: str = scrapy.Field()
    description: str = scrapy.Field()
    upc: str = scrapy.Field()

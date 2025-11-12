# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class BookItem(Item):
    title = Field()
    price = Field()
    amount_in_stock = Field()
    rating = Field()
    category = Field()
    description = Field()
    upc = Field()

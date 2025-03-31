# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksItem(scrapy.Item):
    title = scrapy.Field(serializer=str)
    price = scrapy.Field(serializer=float)
    amount_in_stock = scrapy.Field(serializer=int)
    rating = scrapy.Field(serializer=int)
    description = scrapy.Field(serializer=str)
    category = scrapy.Field(serializer=str)
    upc = scrapy.Field(serializer=str)


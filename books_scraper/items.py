# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksScraperItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    amount_in_stock = scrapy.Field()
    rating = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()
    upc = scrapy.Field()

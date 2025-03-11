# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksScraperItem(scrapy.Item):
    title = scrapy.Field()  # Field for book title
    price = scrapy.Field()  # Field for book price
    amount_in_stock = scrapy.Field()  # Field for amount in stock
    rating = scrapy.Field()  # Field for book rating
    category = scrapy.Field()  # Field for book category
    description = scrapy.Field()  # Field for book description
    upc = scrapy.Field()  # Field for book UPC

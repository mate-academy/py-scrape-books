import scrapy


class BookscraperItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    price = scrapy.Field()
    amount_in_stock = scrapy.Field()
    rating = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()
    upc = scrapy.Field()

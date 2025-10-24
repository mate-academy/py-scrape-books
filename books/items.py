import scrapy


class BooksItem(scrapy.Item):
    title = scrapy.Field(serializer=str)
    price = scrapy.Field(serializer=float)
    amount_in_stock = scrapy.Field(serializer=int)
    rating = scrapy.Field(serializer=int)
    category = scrapy.Field(serializer=str)
    description = scrapy.Field(serializer=str)
    upc = scrapy.Field(serializer=str)

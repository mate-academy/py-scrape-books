import scrapy


def serialize_price(value: str) -> float:
    return float(value.replace("£", ""))


class BookItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field(serializer=serialize_price)
    amount_in_stock = scrapy.Field()
    rating = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()
    upc = scrapy.Field()






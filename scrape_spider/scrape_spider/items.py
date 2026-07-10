from scrapy import Field, Item


class BookItem(Item):
    title = Field()
    price = Field()
    amount_in_stock = Field()
    rating = Field()
    category = Field()
    description = Field()
    upc = Field()

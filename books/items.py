# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def remove_currency_sign(value: str) -> float:
    return float(value.replace("£", ""))


def extrack_amount_int(value: str) -> int:
    return int(value.split()[-2][1:])


def parse_rating(value: str) -> int:
    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }
    return rating_map.get(value.split()[-1], 0)


class BooksItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    price = scrapy.Field(
        input_processor=MapCompose(remove_currency_sign),
        output_processor=TakeFirst()

    )
    amount_in_stock = scrapy.Field(
        input_processor=MapCompose(extrack_amount_int),
        output_processor = TakeFirst()
    )
    rating = scrapy.Field(
        input_processor=MapCompose(parse_rating),
        output_processor=TakeFirst()
    )
    category = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    description = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    upc = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from scrapy_books.items import BookItem
from scrapy_books.spiders.books import BooksSpider


class ScrapyBooksPipeline:
    def process_item(self, item: BookItem, spider: BooksSpider) -> BookItem:

        adapter = ItemAdapter(item)

        # Strip all whitespaces from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != "description":
                value = adapter.get(field_name)
                adapter[field_name] = value[0].strip()

        # Category switch lowercase
        value = adapter.get("category")
        adapter["category"] = value.lower()

        # Price convert to float
        value = adapter.get("price").replace("£", "")
        adapter["price"] = float(value)

        # Amount_in_stock extract number of books in stock
        amount_in_stock_string = adapter.get("amount_in_stock")
        amount_in_stock_string = re.findall(r"\d+", amount_in_stock_string)
        adapter["amount_in_stock"] = int(amount_in_stock_string[0])

        # Rating convert text to number
        rating_string = adapter["rating"]
        rating_string_split = (rating_string.split()[-1]).lower()
        rating_dict = {
            "zero": 0,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5
        }
        adapter["rating"] = rating_dict.get(rating_string_split, None)

        return item

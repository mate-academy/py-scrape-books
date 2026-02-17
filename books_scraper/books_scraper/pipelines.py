# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re


class BooksScraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        required_fields = [
            "title",
            "price",
            "amount_in_stock",
            "rating",
            "category",
            "description",
            "upc",
        ]

        for field in required_fields:
            if not adapter.get(field):
                adapter[field] = None

        price = adapter.get("price")
        if price:
            adapter["price"] = float(price.replace("£", "").strip())

        stock = adapter.get("amount_in_stock")
        if stock:
            match = re.search(r"\d+", stock)
            adapter["amount_in_stock"] = int(match.group()) if match else 0

        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        rating = adapter.get("rating")
        if rating in rating_map:
            adapter["rating"] = rating_map[rating]

        text_fields = ["title", "category", "description", "upc"]

        for field in text_fields:
            value = adapter.get(field)
            if isinstance(value, str):
                adapter[field] = value.strip()

        return item

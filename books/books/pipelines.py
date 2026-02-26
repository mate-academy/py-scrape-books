# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BooksPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        price_raw = adapter.get("price")

        price = None
        if price_raw:
            try:
                price = float(price_raw.replace("£", "").replace(",", "").strip())
            except (ValueError, AttributeError):
                price = None

        adapter["price"] = price

        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        rating_raw = adapter.get("rating")
        adapter["rating"] = rating_map.get(rating_raw)

        if adapter.get("upc") is None:
            adapter["upc"] = ""

        return item

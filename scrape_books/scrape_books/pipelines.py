# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


from itemadapter import ItemAdapter


class ScrapeBooksPipeline:
    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def process_item(self, item, spider):
        if item.get("price"):
            item["price"] = float(item["price"].replace("£", "").strip())

        if item.get("amount_in_stock"):
            try:
                item["amount_in_stock"] = int(item["amount_in_stock"])
            except ValueError:
                item["amount_in_stock"] = 0

        if item.get("rating"):
            item["rating"] = self.RATING_MAP.get(item["rating"], 0)

        return item

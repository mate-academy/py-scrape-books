# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface


class BooksPipeline:
    def process_item(self, item, spider):
        if item.get("price"):
            price_str = item["price"].replace("£", "")
            item["price"] = float(price_str)

        if item.get("amount_in_stock"):
            item["amount_in_stock"] = int(item["amount_in_stock"])

        return item

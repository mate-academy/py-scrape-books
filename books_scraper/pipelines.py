# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BooksScraperPipeline:
    def process_item(self, item, spider):
        item["price"] = float(item["price"].replace("£", ""))
        item["amount_in_stock"] = int(item["amount_in_stock"]) if item["amount_in_stock"] else 0
        item["rating"] = int(item["rating"]) if item["rating"] else None
        item["title"] = item["title"].strip() if item["title"] else "Unknown Title"
        item["description"] = item["description"].strip() if item["description"] else "No description available"
        item["category"] = item["category"].strip() if item["category"] else "Uncategorized"
        return item

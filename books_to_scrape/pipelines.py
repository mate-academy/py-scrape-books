# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from typing import Any

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BooksToScrapePipeline:
    def process_item(self, item: Any, spider: Any) -> Any:
        return item

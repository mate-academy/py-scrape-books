# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from typing import Any

from scrapy import Spider


class EcommercePipeline:
    def process_item(self, item: Any, spider: Spider) -> Any:
        return item

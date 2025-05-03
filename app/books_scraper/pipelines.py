# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
import json
from scrapy import Spider


class AppPipeline:
    def __init__(self):
        self.file = None

    def open_spider(self, spider: Spider):
        self.file = open("books.jl", "w", encoding="utf-8")

    def close_spider(self, spider: Spider):
        if self.file:
            self.file.close()

    def process_item(self, item: scrapy.Item, spider: Spider) -> scrapy.Item:
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

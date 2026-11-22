# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScrappingPipeline:
    def process_item(self, item: dict, spider: scrapy.Spider) -> dict:
        return item

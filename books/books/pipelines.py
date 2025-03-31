# Define your item pipelines here
import scrapy


class BooksPipeline:
    def process_item(
        self,
        item: scrapy.Item,
        spider: scrapy.Spider
    ) -> scrapy.Item:
        return item

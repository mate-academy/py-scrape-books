# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.exporters import JsonItemExporter, JsonLinesItemExporter


class LibraryPipeline:
    def __init__(self) -> None:
        self.file = None
        self.exporter = None

    def open_spider(self, spider: scrapy.Spider) -> None:
        self.file = open("books.jl", "wb")
        self.exporter = JsonLinesItemExporter(self.file, encoding="utf-8")
        self.exporter.start_exporting()

    def close_spider(self, spider: scrapy.Spider) -> None:
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(
        self,
        item: scrapy.Item,
        spider: scrapy.Spider
    ) -> scrapy.Item:
        self.exporter.export_item(item)
        return item

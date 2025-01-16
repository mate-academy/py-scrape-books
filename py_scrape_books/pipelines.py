# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from py_scrape_books.items import PyScrapeBooksItem
# useful for handling different item types with a single interface

from py_scrape_books.spiders.books import BooksSpider


class PyScrapeBooksPipeline:
    def process_item(
            self,
            item: PyScrapeBooksItem,
            spider: BooksSpider
    ) -> PyScrapeBooksItem:
        return item

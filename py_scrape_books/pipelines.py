from scrapy import Spider

from py_scrape_books.items import BookItem


class PyScrapeBooksPipeline:
    def process_item(self, item: BookItem, spider: Spider) -> BookItem:
        return item

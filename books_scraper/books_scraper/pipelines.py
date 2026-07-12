from scrapy import Spider

from books_scraper.items import BookItem


class BooksScraperPipeline:
    def process_item(
        self, item: BookItem, spider: Spider
    ) -> BookItem:
        return item

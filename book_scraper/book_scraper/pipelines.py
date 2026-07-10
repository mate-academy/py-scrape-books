import scrapy
from book_scraper.items import BookScraperItem


class BookScraperPipeline:

    def process_item(
        self, item: BookScraperItem, spider: scrapy.Spider
    ) -> BookScraperItem:
        return item

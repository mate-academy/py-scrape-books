from scrapy import Spider

from book_scraper.items import BookScraperItem


class BookScraperPipeline:
    def process_item(
        self,
        item: BookScraperItem,
        spider: Spider,
    ) -> BookScraperItem:
        return item

from scrapy import Spider, Item


class BookScraperPipeline:
    def process_item(self, item: Item, spider: Spider) -> Item:
        return item

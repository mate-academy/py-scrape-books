import json
from scrapy import Item
from scrapy.spiders import Spider


class JsonLinesPipeline:
    def open_spider(self, spider: Spider) -> None:
        self.file = open("books.jl", "w", encoding="utf-8")

    def process_item(self, item: Item, spider: Spider) -> Item:
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider: Spider) -> None:
        self.file.close()

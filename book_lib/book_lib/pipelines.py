# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import json


class BookLibPipeline:
    def open_spider(self, spider):
        self.file = open('books.jl', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        json.dump(item, self.file, ensure_ascii=False)
        self.file.write('\n')
        return item

    def close_spider(self, spider):
        self.file.close()

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class BooksScraperPipeline:
    def process_item(self, item, spider):
        # Passthrough pipeline — no processing
        return item

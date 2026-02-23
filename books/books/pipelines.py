# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BooksPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        adapter["price"] = float(
            adapter["price"].replace("£", "")
        )

        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        adapter["rating"] = rating_map.get(adapter["rating"], 0)

        return item

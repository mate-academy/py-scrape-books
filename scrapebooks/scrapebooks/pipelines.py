# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from decimal import Decimal


class BookPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        adapter["price"] = Decimal(adapter["price"].replace("£", ""))
        adapter["amount_in_stock"] = int(
            adapter["amount_in_stock"]
            .replace("In stock (", "")
            .replace(" available)", "")
        )
        adapter["rating"] = self.get_rating(
            adapter["rating"].replace("star-rating ", "")
        )

        return item

    def get_rating(self, rating) -> int:
        rating_dict = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        return rating_dict.get(rating, 0)

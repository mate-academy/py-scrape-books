# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.http import Response


class BooksScrapyPipeline:

    num_map = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
    }

    def process_item(self, item, spider) -> dict:
        item["price"] = float(item["price"].strip("£"))
        item["amount_in_stock"] = item["amount_in_stock"].strip()
        item["rating(1-5)"] = self.num_map.get(item["rating(1-5)"].lower(), 0)

        category = item.get("category", [])
        if not category or len(category) < 3:
            item["category"] = "Unknown"
        else:
            item["category"] = category[2]

        return item


def take_description(response: Response) -> str:
    description_block = response.css("div#product_description")
    description = description_block.xpath(
        "following-sibling::p/text()"
    ).get()

    if description:
        return description.strip().replace("...more", "")
    return "No description available"

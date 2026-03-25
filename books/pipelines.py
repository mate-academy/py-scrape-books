# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from word2number import w2n
import re


class BooksPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # --- PRICE ---
        price = adapter.get("price", "")
        adapter["price"] = float(price.replace("£", "")) if price else 0.0

        # --- RATING ---
        rating_class = adapter.get("rating", "")
        rating_word = rating_class.split()[-1] if rating_class else "Zero"
        adapter["rating"] = w2n.word_to_num(rating_word)

        # --- STOCK ---
        stock_list = adapter.get("amount_in_stock", [])
        stock_text = " ".join(stock_list)
        numbers = re.findall(r"\d+", stock_text)
        adapter["amount_in_stock"] = int(numbers[0]) if numbers else 0

        return item

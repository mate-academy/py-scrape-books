# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import re


class BooksScraperPipeline:
    """Pipeline for cleaning and normalizing scraped data."""

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # --- Normalize price ---
        raw_price = adapter.get("price")
        if raw_price:
            cleaned_price = (
                raw_price.replace("£", "")
                .replace(",", "")
                .strip()
            )
            if cleaned_price:
                try:
                    adapter["price"] = float(cleaned_price)
                except ValueError:
                    adapter["price"] = None
            else:
                adapter["price"] = None
        else:
            adapter["price"] = None

        # --- Normalize amount_in_stock ---
        raw_amount = adapter.get("amount_in_stock")
        if raw_amount:
            match = re.search(r"\d+", str(raw_amount))
            if match:
                try:
                    adapter["amount_in_stock"] = int(match.group())
                except ValueError:
                    adapter["amount_in_stock"] = None
            else:
                adapter["amount_in_stock"] = None
        else:
            adapter["amount_in_stock"] = None

        # --- Normalize rating ---
        raw_rating = adapter.get("rating")
        adapter["rating"] = self.RATING_MAP.get(raw_rating)

        # --- Strip description ---
        description = adapter.get("description")
        if description:
            adapter["description"] = description.strip()

        # --- Validate UPC ---
        if not adapter.get("upc"):
            raise DropItem("Missing UPC")

        return item

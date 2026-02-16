import re

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class ScrapeBooksPipeline:
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

        raw_rating = adapter.get("rating")
        adapter["rating"] = self.RATING_MAP.get(raw_rating)

        description = adapter.get("description")
        if description:
            adapter["description"] = description.strip()

        if not adapter.get("upc"):
            raise DropItem("Missing UPC")

        return item

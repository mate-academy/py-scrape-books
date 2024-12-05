from scrapy import Spider
from typing import Any, Dict


RATING: Dict[str, int] = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class ScrapeBooksPipeline:
    def process_item(
            self, item: Dict[str, Any], spider: Spider
    ) -> Dict[str, Any]:
        item["price"] = float(item["price"].replace("£", ""))

        if len(item["amount_in_stock"]) > 0:
            item["amount_in_stock"] = int(
                item["amount_in_stock"][1].replace("\n", "")
                .split()[2].replace("(", "")
            )
        else:
            item["amount_in_stock"] = 0

        item["rating"] = RATING[item["rating"].split()[1]]

        return item

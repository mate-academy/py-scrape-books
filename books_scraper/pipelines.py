from typing import Any

from scrapy import Item, Spider


def process_item(self: Any, item: Item, spider: Spider) -> Item:
    # Example 1: Clean the title by stripping leading/trailing spaces
    if "title" in item:
        item["title"] = item["title"].strip()

    # Example 2: Check if the price is valid (e.g., is it a non-empty string?)
    if "price" in item:
        item["price"] = item["price"].strip() \
            if item["price"] else "Unknown Price"

    # Example 3:
    # Ensure the amount in stock is an integer or set to 0 if invalid
    if "amount_in_stock" in item:
        try:
            item["amount_in_stock"] = int(item["amount_in_stock"])
        except ValueError:
            item["amount_in_stock"] = 0  # Default value if conversion fails

    # You can add more processing logic as needed,
    # such as validation or cleaning for other fields

    # Return the processed item
    return item

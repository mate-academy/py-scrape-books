from itemadapter import ItemAdapter


class BooksPipeline:
    RATING_MAP = {
        "Zero": 0,
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        price_raw = adapter.get("price")
        if price_raw:
            adapter["price"] = float(price_raw.replace("£", "").strip())
        else:
            adapter["price"] = 0.0

        stock_raw = adapter.get("amount_in_stock")
        adapter["amount_in_stock"] = int(stock_raw) if stock_raw else 0

        rating_raw = adapter.get("rating")
        if rating_raw:
            rating_word = rating_raw.split()[-1]
            adapter["rating"] = self.RATING_MAP.get(rating_word, 0)
        else:
            adapter["rating"] = 0

        for field in ["title", "category", "description", "upc"]:
            value = adapter.get(field)
            if value:
                adapter[field] = value.strip()

        return item

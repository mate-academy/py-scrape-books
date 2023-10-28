from itemadapter import ItemAdapter


class BooksScrapePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        """strip all whitespaces from strings"""
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != "description":
                value = adapter.get(field_name)
                adapter[field_name] = value[0].strip()

        """category --> switch to lowercase"""
        value = adapter.get("category")
        adapter["category"] = value.lower()

        """price --> convert to float"""
        value = adapter.get("price")
        value = value.replace("£", "")
        adapter["price"] = float(value)

        """amount_in_stock --> extract number of books in stock"""
        amount_in_stock_string = adapter.get("amount_in_stock")
        split_string_array = amount_in_stock_string.split("(")
        if len(split_string_array) < 2:
            adapter["amount_in_stock"] = 0
        else:
            amount_in_stock_array = split_string_array[1].split(" ")
            adapter["amount_in_stock"] = int(amount_in_stock_array[0])

        """Rating --> convert text to number"""
        rating_string = adapter.get("rating")
        split_rating_array = rating_string.split(" ")
        rating_text_value = split_rating_array[1].lower()
        if rating_text_value == "zero":
            adapter["rating"] = 0
        elif rating_text_value == "one":
            adapter["rating"] = 1
        elif rating_text_value == "two":
            adapter["rating"] = 2
        elif rating_text_value == "three":
            adapter["rating"] = 3
        elif rating_text_value == "four":
            adapter["rating"] = 4
        elif rating_text_value == "five":
            adapter["rating"] = 5

        return item

import re


def clean_price(price_str):
    if price_str:
        return float(price_str.replace("£", ""))
    return None


def extract_stock_number(stock_str):
    if stock_str:
        match = re.search(r"\((\d+)\s+available\)", stock_str)
        if match:
            return int(match.group(1))
    return 0


def convert_rating(rating_class):
    ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    if rating_class:
        for rating in ratings:
            if rating in rating_class:
                return ratings[rating]
    return None

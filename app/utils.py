import re


def clean_price(price_str):
    if price_str:
        price_str = price_str.replace("\xa0", " ").strip()
        return float(price_str.replace("£", ""))
    return None


def extract_stock_number(stock_str):
    if stock_str:
        match = re.search(r"\((\d+)\s+available\)", stock_str, re.IGNORECASE)
        if match:
            return int(match.group(1))
        digits = re.search(r"(\d+)", stock_str)
        if digits:
            return int(digits.group(1))
    return 0


def convert_rating(rating_class):
    ratings = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    if rating_class:
        classes = rating_class.lower().split()
        for cls in classes:
            if cls in ratings:
                return ratings[cls]
    return None

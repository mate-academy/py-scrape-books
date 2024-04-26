RATINGS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def convert_to_int(rating: str) -> int:
    return RATINGS[rating]

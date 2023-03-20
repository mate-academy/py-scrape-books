from scrapy.http import HtmlResponse


def get_rating(response: HtmlResponse) -> int:
    help_dict = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    rating_class = response.css(
        ".product_main p.star-rating::attr(class)"
    ).get()
    rating = help_dict.get(rating_class.split()[-1])
    return rating


def parse_book_details(response: HtmlResponse) -> None:
    title = response.css(".product_main h1::text").get()
    price = response.css(
        ".product_main .price_color::text"
    ).get().replace("£", "")
    amount_in_stock = response.css(
        ".product_main .availability::text"
    ).re_first(r"(\d+) available")
    category = response.css(
        ".breadcrumb li:nth-last-child(2) a::text"
    ).get()
    description = response.css("#product_description + p::text").get()
    upc = response.xpath(
        "//th[text()='UPC']/following-sibling::td/text()"
    ).get()

    yield {
        "title": title,
        "price": price,
        "amount_in_stock": amount_in_stock,
        "category": category,
        "rating": get_rating(response),
        "description": description,
        "upc": upc,
    }

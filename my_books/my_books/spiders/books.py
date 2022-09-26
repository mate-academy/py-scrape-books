import scrapy
from scrapy.http import Response


def extract_numbers_from_amount(string):
    result = ""
    for char in string:
        if char.isnumeric():
            result += char
    return int(result)


def extract_rating(string):
    string = string.split("=")[1]
    if "One" in string:
        return 1
    if "Two" in string:
        return 2
    if "Three" in string:
        return 3
    if "Four" in string:
        return 4
    if "Five" in string:
        return 5


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse_book(self, book: Response):
        yield {
            "title": book.css(".product_main > h1::text").get(),
            "price": float(book.css(".price_color::text").get().replace("£", "")),
            "amount_in_stock": extract_numbers_from_amount(
                book.css("tr:nth-child(6) td::text").get()
            ),
            "rating": extract_rating(book.css(".star-rating").get()),
            "category": book.css(
                ".breadcrumb > li:nth-child(3) > a::text").get(),
            "description": book.css(".sub-header + p::text").get(),
            "upc": book.css("tr:nth-child(1) td::text").get(),
        }

    def parse(self, response: Response, **kwargs):
        for book in response.css(".col-lg-3").css("a::attr(href)"):
            yield scrapy.Request(
                response.urljoin(book.get()), callback=self.parse_book
            )

        next_page = response.css(".next a::attr(href)").get()

        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

import re

import scrapy
from scrapy.http import Response

RATINGS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        "FEEDS": {
            "books.jl": {"format": "jsonlines", "overwrite": True},
        },
    }

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css("article.product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> dict:
        yield {
            "title": self.parse_title(response),
            "price": self.parse_price(response),
            "amount_in_stock": self.parse_amount_in_stock(response),
            "rating": self.parse_rating(response),
            "category": self.parse_category(response),
            "description": self.parse_description(response),
            "upc": self.parse_upc(response),
        }

    @staticmethod
    def parse_title(response: Response) -> str:
        return response.css("h1::text").get()

    @staticmethod
    def parse_price(response: Response) -> float:
        price = response.css("p.price_color::text").get()
        return float(re.findall(r"[\d.]+", price)[0])

    @staticmethod
    def parse_amount_in_stock(response: Response) -> int:
        amount = response.css(
            "p.instock.availability::text"
        ).re_first(r"\d+")
        return int(amount) if amount else 0

    @staticmethod
    def parse_rating(response: Response) -> int:
        rating_word = response.css(
            "p.star-rating::attr(class)"
        ).get().split()[-1]
        return RATINGS.get(rating_word, 0)

    @staticmethod
    def parse_category(response: Response) -> str:
        return response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get()

    @staticmethod
    def parse_description(response: Response) -> str:
        return response.css("#product_description ~ p::text").get()

    @staticmethod
    def parse_upc(response: Response) -> str:
        return response.css(
            "table.table-striped tr:nth-child(1) td::text"
        ).get()

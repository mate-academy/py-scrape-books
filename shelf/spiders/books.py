import re

import scrapy
from scrapy.http import Response

RATING = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> dict:
        for book_card in response.css("article.product_pod"):
            yield response.follow(
                book_card.css("a::attr(href)").get(),
                callback=self.parse_book_detail
            )

        if next_href := response.css("li.next a::attr(href)").get():
            yield response.follow(next_href, callback=self.parse)

    def parse_book_detail(self, response: Response) -> dict:
        product_detail = dict(
            zip(
                response.css("table tr th::text").getall(),
                response.css("table tr td::text").getall()
            )
        )

        yield {
            "title": self.get_title(response),
            "category": self.get_category(product_detail),
            "upc": self.get_upc(product_detail),
            "price": self.get_price(response),
            "rating": self.get_rating(response),
            "description": self.get_description(response),
            "amount_in_stock": self.get_amount_in_stock(product_detail),
        }

    @staticmethod
    def get_title(response: Response) -> str:
        return response.css(".product_main h1::text").get()

    @staticmethod
    def get_category(product_detail: dict) -> str:
        return product_detail.get("Product Type")

    @staticmethod
    def get_upc(product_detail: dict) -> str:
        return product_detail.get("UPC")

    @staticmethod
    def get_price(response: Response) -> str:
        return response.css(".product_main p.price_color::text").get()[1:]

    @staticmethod
    def get_rating(response: Response) -> int | None:
        return RATING.get(
            response.css("p.star-rating::attr(class)").get().split()[-1]
        )

    @staticmethod
    def get_description(response: Response) -> str:
        return response.css("#product_description ~ p::text").get()

    @staticmethod
    def get_amount_in_stock(product_detail: dict) -> int:
        return int(re.sub(
            "\D", "",  # NOQA W605
            product_detail.get("Availability")
        ))

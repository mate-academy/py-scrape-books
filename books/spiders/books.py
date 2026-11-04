import re
from typing import Iterator

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

    def parse(self, response: Response, **kwargs) -> Iterator:
        for book in response.css("article.product_pod h3 a"):
            yield response.follow(
                book, callback=self.parse_book
            )

        next_page = response.css("li.next a")
        if next_page:
            yield response.follow(next_page[0], callback=self.parse)

    def parse_book(self, response: Response) -> dict:
        return {
            "title": response.css("div.product_main h1::text").get(),
            "price": float(
                response.css("p.price_color::text").get().lstrip("£Â")
            ),
            "amount_in_stock": self._parse_stock(response),
            "rating": self._parse_rating(response),
            "category": response.css(
                "ul.breadcrumb li:nth-child(3) a::text"
            ).get(),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": response.css(
                "table.table-striped tr:first-child td::text"
            ).get(),
        }

    @staticmethod
    def _parse_stock(response: Response) -> int:
        text = " ".join(
            response.css("p.availability::text").getall()
        )
        match = re.search(r"\((\d+) available\)", text)
        return int(match.group(1)) if match else 0

    @staticmethod
    def _parse_rating(response: Response) -> int:
        classes = response.css("p.star-rating::attr(class)").get()
        return RATINGS[classes.split()[-1]]

import re
from collections.abc import Iterator
from typing import Any

import scrapy
from scrapy.http import Response

from books_scraper.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"

    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    rating_values = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(
        self,
        response: Response,
        **kwargs: Any,
    ) -> Iterator[scrapy.Request]:
        book_links = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()

        for book_link in book_links:
            yield response.follow(
                url=book_link,
                callback=self.parse_book,
            )

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(
                url=next_page,
                callback=self.parse,
            )

    def parse_book(self, response: Response) -> BookItem:
        return BookItem(
            title=self.parse_title(response),
            price=self.parse_price(response),
            amount_in_stock=self.parse_amount_in_stock(response),
            rating=self.parse_rating(response),
            category=self.parse_category(response),
            description=self.parse_description(response),
            upc=self.parse_upc(response),
        )

    @staticmethod
    def parse_title(response: Response) -> str:
        return response.css(
            "div.product_main h1::text"
        ).get(default="").strip()

    @staticmethod
    def parse_price(response: Response) -> float:
        price_text = response.css(
            "p.price_color::text"
        ).get(default="")

        normalized_price = price_text.replace("£", "").strip()

        return float(normalized_price)

    @staticmethod
    def parse_amount_in_stock(response: Response) -> int:
        availability = response.xpath(
            '//th[text()="Availability"]/following-sibling::td/text()'
        ).get(default="")

        match = re.search(r"\d+", availability)

        return int(match.group()) if match else 0

    def parse_rating(self, response: Response) -> int:
        rating_classes = response.css(
            "p.star-rating::attr(class)"
        ).get(default="").split()

        rating_name = next(
            (
                class_name
                for class_name in rating_classes
                if class_name in self.rating_values
            ),
            "",
        )

        return self.rating_values.get(rating_name, 0)

    @staticmethod
    def parse_category(response: Response) -> str:
        return response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get(default="").strip()

    @staticmethod
    def parse_description(response: Response) -> str:
        description = response.css(
            "#product_description + p::text"
        ).get(default="").strip()

        return description or "No description available."

    @staticmethod
    def parse_upc(response: Response) -> str:
        return response.xpath(
            '//th[text()="UPC"]/following-sibling::td/text()'
        ).get(default="").strip()

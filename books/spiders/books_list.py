from collections.abc import Iterator
from typing import Any

import scrapy
from scrapy.http import Response

from books.items import BooksItem



RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksListSpider(scrapy.Spider):
    name = "books_list"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs: Any) -> Iterator[scrapy.Request]:
        for href in response.css(
                "article.product_pod h3 a::attr(href)"
        ).getall():
            yield response.follow(href, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> Iterator[BooksItem]:
        yield BooksItem(
            title=response.css("h1::text").get(),
            price=self._parse_price(response),
            amount_in_stock=self._parse_stock(response),
            rating=self._parse_rating(response),
            category=response.css("ul.breadcrumb li:nth-child(3) a::text").get(),
            description=response.css("#product_description + p::text").get(),
            upc=self._parse_upc(response),
        )

    @staticmethod
    def _table_value(response: Response, name: str) -> str | None:
        return response.xpath(
            "//th[normalize-space()='{name}']/following-sibling::td/text()",
            name=name,
        ).get()

    @staticmethod
    def _parse_price(response: Response) -> float | None:
        price = response.css("p.price_color::text").re_first(r"[\d.]+")
        return float(price) if price else None

    @staticmethod
    def _parse_stock(response: Response) -> int | None:
        stock = response.css("p.availability").re_first(r"\((\d+) available\)")
        return int(stock) if stock else 0

    @staticmethod
    def _parse_rating(response: Response) -> int:
        classes = response.css("p.star-rating::attr(class)").get()
        return RATING_MAP.get(classes.split()[-1], 0) if classes else 0

    @staticmethod
    def _parse_upc(response: Response) -> str | None:
        return response.css("table td::text").get()

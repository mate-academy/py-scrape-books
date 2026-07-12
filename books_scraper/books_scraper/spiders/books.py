import re
from typing import Generator, Optional

import scrapy
from scrapy.http import Response

from books_scraper.items import BookItem

RATING_MAP = {
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

    def parse(
        self, response: Response
    ) -> Generator[scrapy.Request, None, None]:
        category_links = response.css(
            ".nav-list ul li a::attr(href)"
        ).getall()
        for category_link in category_links:
            yield response.follow(
                category_link, callback=self.parse_category
            )

    def parse_category(
        self, response: Response
    ) -> Generator[scrapy.Request, None, None]:
        book_links = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()
        for book_link in book_links:
            yield response.follow(book_link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(
                next_page, callback=self.parse_category
            )

    @staticmethod
    def _extract_amount_in_stock(response: Response) -> int:
        availability_lines = response.css(
            "p.availability::text"
        ).getall()
        availability_text = (
            availability_lines[-1] if availability_lines else ""
        )
        amount_match = re.search(r"\d+", availability_text)
        return int(amount_match.group()) if amount_match else 0

    @staticmethod
    def _extract_rating(response: Response) -> int:
        rating_class = response.css("p.star-rating::attr(class)").get()
        if not rating_class:
            return 0
        class_parts = rating_class.split()
        rating_word = class_parts[-1] if class_parts else ""
        return RATING_MAP.get(rating_word, 0)

    def parse_book(
        self, response: Response
    ) -> Generator[BookItem, None, None]:
        price_text = response.css(
            "p.price_color::text"
        ).get(default="£0")

        description = response.css(
            "#product_description ~ p::text"
        ).get(default="")

        upc_value: Optional[str] = response.css(
            "table.table.table-striped tr:first-child td::text"
        ).get()

        yield BookItem(
            title=response.css(".product_main h1::text").get(),
            price=float(re.sub(r"[^\d.]", "", price_text) or 0),
            amount_in_stock=self._extract_amount_in_stock(response),
            rating=self._extract_rating(response),
            category=response.css(
                "ul.breadcrumb li:nth-child(3) a::text"
            ).get(),
            description=description.strip(),
            upc=upc_value,
        )

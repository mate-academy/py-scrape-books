
import re
from collections.abc import Generator

import scrapy

from books.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(
        self,
        response: scrapy.http.Response,
    ) -> Generator[scrapy.Request, None, None]:
        """
        Parse catalog pages and follow book and pagination links.
        """

        book_links = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()

        for book_link in book_links:
            yield response.follow(
                book_link,
                callback=self.parse_book,
            )

        next_page = response.css(
            "li.next a::attr(href)"
        ).get()

        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse,
            )

    def parse_book(
        self,
        response: scrapy.http.Response,
    ) -> Generator[BookItem, None, None]:
        """
        Parse information from an individual book page.
        """

        item = BookItem()

        # Title
        item["title"] = response.css(
            "div.product_main h1::text"
        ).get(default="").strip()

        # Price
        item["price"] = response.css(
            "p.price_color::text"
        ).get(default="").strip()

        # Amount in stock
        availability = response.css(
            "p.instock.availability::text"
        ).getall()

        availability_text = " ".join(
            text.strip() for text in availability
        )

        stock_match = re.search(
            r"\((\d+)\s+available\)",
            availability_text,
        )

        item["amount_in_stock"] = (
            int(stock_match.group(1))
            if stock_match
            else 0
        )

        # Rating
        rating_classes = response.css(
            "p.star-rating::attr(class)"
        ).get(default="")

        rating_mapping = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        item["rating"] = next(
            (
                value
                for word, value in rating_mapping.items()
                if word in rating_classes.split()
            ),
            0,
        )

        # Category
        item["category"] = response.css(
            "ul.breadcrumb li:nth-last-child(2) a::text"
        ).get(default="").strip()

        # Description
        item["description"] = response.css(
            "#product_description + p::text"
        ).get(default="").strip()

        # UPC
        item["upc"] = response.xpath(
            "//th[normalize-space()='UPC']"
            "/following-sibling::td/text()"
        ).get(default="").strip()

        yield item

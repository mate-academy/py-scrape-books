import re
from typing import Generator

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(
        self,
        response: Response,
    ) -> Generator[scrapy.Request, None, None]:
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
        response: Response,
    ) -> Generator[dict, None, None]:
        title = response.css(
            "div.product_main h1::text"
        ).get()

        price_text = response.css(
            "p.price_color::text"
        ).get()

        stock_parts = response.css(
            "p.instock.availability::text"
        ).getall()

        stock_text = " ".join(
            part.strip()
            for part in stock_parts
            if part.strip()
        )

        stock_match = re.search(
            r"\((\d+) available\)",
            stock_text,
        )

        amount_in_stock = (
            int(stock_match.group(1))
            if stock_match
            else 0
        )

        rating_class = response.css(
            "p.star-rating::attr(class)"
        ).get()

        rating_name = (
            rating_class.split()[-1]
            if rating_class
            else ""
        )

        rating = self.rating_map.get(
            rating_name,
            0,
        )

        category = response.css(
            "ul.breadcrumb li:nth-last-child(2) a::text"
        ).get()

        description = response.css(
            "#product_description + p::text"
        ).get()

        upc = self.get_product_information(
            response,
            "UPC",
        )

        price = (
            float(
                price_text
                .replace("£", "")
                .strip()
            )
            if price_text
            else 0.0
        )

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }

    @staticmethod
    def get_product_information(
        response: Response,
        field_name: str,
    ) -> str | None:
        rows = response.css(
            "table.table.table-striped tr"
        )

        for row in rows:
            header = row.css(
                "th::text"
            ).get()

            if header == field_name:
                return row.css(
                    "td::text"
                ).get()

        return None

import re
from collections.abc import Iterable

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"

    allowed_domains = ["books.toscrape.com"]

    start_urls = [
        "https://books.toscrape.com/"
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "AUTOTHROTTLE_ENABLED": True,
        "ROBOTSTXT_OBEY": True,
    }

    RATINGS = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def parse(
            self,
            response: Response
    ) -> Iterable[scrapy.Request]:
        book_links = response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall()

        for link in book_links:
            yield response.follow(
                link,
                callback=self.parse_book
            )

        next_page = response.css(
            "li.next a::attr(href)"
        ).get()

        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse
            )

    def parse_book(
            self,
            response: Response
    ) -> Iterable[dict[str, str | int | float]]:
        title = response.css(
            ".product_main h1::text"
        ).get()

        price_text = response.css(
            ".product_main .price_color::text"
        ).get()

        availability = response.css(
            ".product_main .availability::text"
        ).getall()

        stock_text = " ".join(availability)

        stock_match = re.search(
            r"\((\d+) available\)",
            stock_text
        )

        amount_in_stock = (
            int(stock_match.group(1))
            if stock_match else 0
        )

        rating_class = response.css(
            ".product_main .star-rating::attr(class)"
        ).get(default="")

        rating = next(
            (
                value
                for name, value in self.RATINGS.items()
                if name in rating_class.split()
            ),
            0,
        )

        category = response.css(
            ".breadcrumb li:nth-last-child(2) a::text"
        ).get()

        description = response.css(
            "#product_description + p::text"
        ).get(default="")

        upc = response.xpath(
            '//th[text()="UPC"]/following-sibling::td/text()'
        ).get()

        price = float(
            re.sub(r"[^\d.]", "", price_text)
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

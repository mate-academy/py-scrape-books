import re

import scrapy
from scrapy.http import Response


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_url = book.css("h3 a::attr(href)").get()

            yield response.follow(
                book_url,
                callback=self.parse_book,
            )

        next_page = response.css(".next a::attr(href)").get()

        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse,
            )

    def parse_book(self, response: Response):

        availability = response.css(
            ".product_main .availability"
        ).xpath("string(.)").get()

        availability = availability.strip() if availability else ""

        amount_in_stock = re.search(r"\d+", availability)

        yield {
            "title": response.css(
                ".product_main h1::text"
            ).get(),

            "price": response.css(
                ".product_main .price_color::text"
            ).get(),

            "amount_in_stock": (
                int(amount_in_stock.group())
                if amount_in_stock
                else None
            ),
            "rating": response.css(
                ".product_main .star-rating::attr(class)"
            ).get().split()[-1],

            "category": response.css(
                ".breadcrumb li:nth-child(3) a::text"
            ).get(),

            "description": response.css(
                "#product_description + p::text"
            ).get(),

            "upc": response.css(
                ".table.table-striped tr:nth-child(1) td::text"
            ).get(),
        }

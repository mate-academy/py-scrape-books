from pathlib import Path

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        "https://books.toscrape.com/"
    ]

    def parse(self, response: Response, **kwargs):
        for book in response.css("article.product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response):
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }

        amount_in_stock = int("".join(filter(
            str.isdigit,
            response.css(
                ".table-striped tr:contains('Availability') td::text"
            ).get())))
        rating = rating_map.get(
            response.css("p.star-rating::attr(class)"
                         )
            .get()
            .split()[-1], 0
        )
        category = response.css(
            ".breadcrumb li:nth-child(3) a::text"
        ).get().strip()
        description = response.css("#product_description ~ p::text").get()
        ups = response.css(
                ".table-striped tr:contains('UPC') td::text"
            ).get()

        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": response.css(
                ".product_main .price_color::text"
            )
            .get()
            .replace("£", ""),
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": ups
        }

from typing import Any

import scrapy
from scrapy.http import Response

STR_TO_INT = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]

    def parse(self, response: Response, **kwargs: Any):
        pass
        for book in response.css(".product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("ul.pager li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response, **kwargs: Any):
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": float(
                response.css(".product_main p.price_color::text")
                .get()
                .replace("£", "")
            ),
            "amount_in_stock": int(
                response.css(".product_main p.instock::text")
                .getall()[1]
                .replace("(", "")
                .strip()
                .split()[2]
            ),
            "rating": STR_TO_INT[
                response.css(".product_main p.star-rating::attr(class)")
                .get()
                .split(" ")[-1]
            ],
            "category": response.css(
                "ul.breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "UPC": response.css("table.table tr:first-child td::text").get(),
        }

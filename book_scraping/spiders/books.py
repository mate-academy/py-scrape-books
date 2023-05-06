from typing import Generator

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Generator:
        for book in response.css(".product_pod > h3 > a::attr(href)").getall():
            yield response.follow(book, self.parse_book)

        next_page = response.css(".next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response: Response) -> Generator:
        def rating_convert(rating: str) -> int:
            ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
            return ratings.get(rating, 0)

        yield {
            "title": response.css("h1::text").get(),
            "price": response.css(".price_color::text").get(),
            "amount_in_stock": "".join(filter(str.isdigit, response.css(
                "tr:contains('Availability') td::text"
            ).get())),
            "rating": rating_convert(
                response.css(".star-rating::attr(class)"
                             ).get().split()[1]),
            "category": response.css(
                ".breadcrumb > li:nth-child(3) > a::text"
            ).get(),
            "description": response.css(
                "#product_description ~ p::text"
            ).get(),
            "upc": response.css("tr:contains('UPC') td::text").get(),
        }

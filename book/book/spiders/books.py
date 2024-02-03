from typing import Any, NoReturn

import scrapy
from scrapy.http import Response, Request


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs: Any) -> NoReturn:
        book_links = response.css("h3 a::attr(href)").extract()

        for link in book_links:
            yield Request(url=response.urljoin(link), callback=self.parse_book)

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_book(response: Response) -> NoReturn:
        book_rating = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        yield {
            "title": response.css("h1::text").get(),
            "price": float(
                response.css(".price_color::text").get().replace("£", "")
            ),
            "amount_in_stock": int(
                response.css("tr:contains('Availability') td::text")
                .get()
                .split()[2]
                .replace("(", "")
            ),
            "rating": book_rating.get(
                response.css(".star-rating::attr(class)").get().split()[1]
            ),
            "category": response.css(".breadcrumb > li > a::text").getall()[2],
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": response.css("tr:contains('UPC') td::text").get(),
        }

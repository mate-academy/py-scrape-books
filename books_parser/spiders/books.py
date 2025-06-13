from typing import Generator

import scrapy
from scrapy import Request
from scrapy.http import Response

from books_parser.items import BooksParserItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse_book_page(
        self, response: Response, **kwargs
    ) -> Generator[BooksParserItem, None, None]:

        rating_str_to_int = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        yield BooksParserItem(
            title=response.css(".product_main > h1::text").get(),
            price=float(
                response.css(".product_main > .price_color::text")
                .get()
                .replace("£", "")
            ),
            amount_in_stock=int(
                response.css(".instock")
                .re_first("\d+ available")  # noqa: W605
                .split()[0]
            ),
            rating=rating_str_to_int[
                response.css(".star-rating::attr(class)").get().split()[-1]
            ],
            category=response.css(".breadcrumb > li > a::text")[-1].get(),
            description=response.css("#product_description + p::text").get(),
            upc=response.css(".table tr td::text")[0].get(),
        )

    def parse(
        self, response: Response, **kwargs
    ) -> Generator[BooksParserItem | Request, None, None]:
        book_pages = [
            book_link.get()
            for book_link in response.css(".product_pod h3 > a::attr(href)")
        ]

        for book_page in book_pages:
            yield response.follow(book_page, callback=self.parse_book_page)

        next_page = response.css("li.next > a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

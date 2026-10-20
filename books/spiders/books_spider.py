from typing import Iterator

import scrapy
from scrapy import Request
from scrapy.http import Response

from books.items import BooksItem


class BooksSpider(scrapy.Spider):
    name = "books_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    rating = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def follow_next_page(self, response: Response) -> Iterator[Request]:
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def get_rating(self, response: Response) -> int:
        rating = response.css("p.star-rating::attr(class)").get()
        word = rating.replace("star-rating", "").strip()
        return self.rating.get(word, 0)

    def parse(self, response: Response, **kwargs) -> Iterator[Request]:
        for href in response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall():
            yield response.follow(href, callback=self.parse_book)

        yield from self.follow_next_page(response)

    def parse_book(self, response: Response, **kwargs) -> Iterator[BooksItem]:
        yield BooksItem(
            title=response.css("h1::text").get(),
            price=float(
                response.css("div.product_main p.price_color::text")
                .get(default="0")
                .replace("£", "")
            ),
            amount_in_stock=int(
                response.css("p.availability::text").re_first(r"\d+", default="0")
            ),
            rating=self.get_rating(response),
            category=response.css(
                "ul.breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            description=response.css("#product_description + p::text").get(),
            upc=response.css("table tr:first-child td::text").get(),
        )

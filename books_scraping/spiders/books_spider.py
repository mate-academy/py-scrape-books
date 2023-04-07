from typing import Generator

import scrapy
from scrapy.http import Response

from books_scraping.items import Book


class BooksSpider(scrapy.Spider):
    name = "books"
    base_url = "https://books.toscrape.com/catalogue/"

    def start_requests(self) -> Generator:
        start_url = self.base_url + "page-1.html"
        yield scrapy.Request(
            url=start_url,
            callback=self.get_books_links_from_page
        )

    def get_books_links_from_page(self, response: Response) -> Generator:
        for book_url in response.css(".product_pod h3 a::attr(href)").getall():
            yield response.follow(
                self.base_url + book_url,
                callback=self.parse
            )

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(
                self.base_url + "/" + next_page,
                callback=self.get_books_links_from_page
            )

    def parse(self, response: Response, **kwargs) -> Book:
        ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

        yield Book(
            title=response.css("h1::text").get(),
            price=float(response.css("p.price_color::text").get()
                        .replace("£", "")),
            amount_in_stock=int(response.css(".table-striped tr td::text")
                                .getall()[-2].replace("(", "").split()[-2]),
            rating=ratings[
                response.css(
                    ".star-rating"
                ).xpath("@class").extract()[0].split()[-1]
            ],
            category=response.css(".breadcrumb li a::text").getall()[-1],
            description=response.css("article > p::text").get(),
            upc=response.css(".table-striped tr td::text").getall()[0]
        )

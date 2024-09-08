from typing import Generator

import scrapy
from scrapy.http import Response


class BooksDetailsSpider(scrapy.Spider):
    name = "books_details"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def get_rating(self, book: Response) -> int:
        ratings = book.css("p.star-rating::attr(class)").get().split()
        rating = ratings[1]
        values = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        return values.get(rating, "-")

    def parse_one_book(self, response: Response) -> dict:
        book = {
            "title": response.css("div.product_main h1::text").get(),
            "price": float(
                str(response.css(".price_color::text").get()).replace("£", "")
            ),
            "amount_in_stock": response.css("p.instock.availability::text")
            .getall()[-1]
            .strip(),
            "rating": self.get_rating(response),
            "category": response.css(".breadcrumb > li > a::text").get(),
            "description": response.css("#product_description ~ p::text")
            .get()[:-9],
            "upc": response.css("tr > td::text").get(),
        }
        return book

    def parse(self, response: Response, **kwargs) -> Generator:
        for book in response.css(".product_pod"):
            url = book.css("h3 > a::attr(href)").get()
            if url is not None:
                book_url = response.urljoin(url)
                yield scrapy.Request(book_url, callback=self.parse_one_book)

        next_page = response.css("li.next a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

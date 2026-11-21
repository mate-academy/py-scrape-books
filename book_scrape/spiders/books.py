from typing import Generator

import scrapy
from scrapy.http import Response


numbers = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> Generator:
        for book in response.css(".product_pod"):
            href = book.css("a::attr(href)").get()
            book_page = response.follow(href, callback=self.parse_book)

            yield book_page

        next_page = response.css(".pager .next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> Generator:

        title = response.css(".product_main h1::text").get()

        price = float(response.css(".price_color::text").get()[1:])

        amount_in_stock = int(
            response.css(".product_main .instock::text")[-1].get()
            .split()[2][1:]
        )

        rating = numbers[
            response.css(".star-rating::attr(class)").get().split()[1]
        ]

        category = response.css(".breadcrumb").css("a::text")[2].get()

        description = (
            response.css("#product_description")
            .xpath("./following-sibling::p[1]/text()").get()
        )

        upc = response.css("table td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
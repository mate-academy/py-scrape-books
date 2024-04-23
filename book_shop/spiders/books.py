from enum import Enum

import scrapy
from scrapy.http import Response


class Rating(Enum):
    Zero = 0
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def get_amount_in_stock(amount_str: str) -> int:
        return int("".join((
            num
            for num in amount_str
            if num.isnumeric()
        )))

    def parse_book(self, response: Response) -> dict:
        return {
            "title": response.css(".product_main h1::text").get(),
            "price": response.css(".price_color::text").get().replace("£", ""),
            "amount_in_stock": self.get_amount_in_stock(response.css(".table td::text").getall()[-2]),
            "rating": Rating[response.css(".star-rating::attr(class)").get().split(" ")[-1]].value,
            "category": response.css(".breadcrumb li a::text").getall()[-1],
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table td::text").get()
        }

    def parse(self, response: Response, *args, **kwargs):
        books_links = response.css("li h3 a::attr(href)").getall()

        yield from response.follow_all(books_links, callback=self.parse_book)

        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

from typing import Any

import scrapy
from scrapy.exceptions import CloseSpider


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    books_limit = 1000
    books_count = 0

    def parse(self, response: Any) -> Any:
        for book in response.css("article.product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Any) -> Any:
        if self.books_count >= self.books_limit:
            raise CloseSpider("Reached 1000 books")
        self.books_count += 1

        yield {
            "title": response.css("h1::text").get(),
            "price": self.parse_price(response),
            "amount_in_stock": self.parse_amount_in_stock(response),
            "rating": self.parse_rating(response),
            "category": response.css(
                ".breadcrumb li:nth-child(3) a::text"
            ).get(),
            "description": response.css(
                "#product_description ~ p::text"
            ).get(),
            "upc": response.css(
                "table.table tr:nth-child(1) td::text"
            ).get(),
        }

    @staticmethod
    def parse_price(response: Any) -> float:
        price = response.css(".price_color::text").get()
        return float(price.replace("£", ""))

    @staticmethod
    def parse_rating(response: Any) -> str:
        rating = response.css(".star-rating::attr(class)").get()
        return rating.split()[-1]

    @staticmethod
    def parse_amount_in_stock(response: Any) -> int:
        stock = response.css(".instock.availability::text").getall()
        digits = "".join(filter(str.isdigit, "".join(stock)))
        return int(digits) if digits else 0

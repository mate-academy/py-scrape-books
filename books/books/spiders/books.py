from typing import Generator

import scrapy
from scrapy.http import Response, Request


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(
            self,
            response: Response,
            **kwargs
    ) -> Generator[Request, None, None]:
        books = response.css(".product_pod")
        for book in books:
            if book.css("h3 a::attr(href)").get():
                yield response.follow(
                    book.css("h3 a::attr(href)").get(),
                    callback=self.parse_book
                )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page)

    def parse_book(
            self,
            response: Response
    ) -> Generator[dict, None, None]:
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": self.extract_price(response),
            "amount_in_stock": self.extract_stock_amount(response),
            "rating": self.extract_rating(response),
            "category": response.css(".breadcrumb > li:nth-child(3) a::text").get(),
            "description": response.css("#product_description + p::text").get(),
            "upc": response.css(".table tr:nth-child(1) td::text").get(),
        }

    @staticmethod
    def extract_price(response: Response) -> float:
        price_text = response.css(".price_color::text").get()
        return float(price_text.replace("£", "")) if price_text else 0.0

    @staticmethod
    def extract_stock_amount(response: Response) -> int:
        stock_text = response.css(".instock.availability::text").re_first(r"\d+")
        return int(stock_text) if stock_text else 0

    @staticmethod
    def extract_rating(response: Response) -> str:
        return response.css("p.star-rating::attr(class)").re_first(r"star-rating (\w+)") or "Not rated"

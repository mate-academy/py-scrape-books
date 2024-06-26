import re
import scrapy

from scrapy.http import Response
from word2number.w2n import word_to_num


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    @staticmethod
    def parse_title(response: Response) -> str:
        return response.css(".product_main > h1::text").get()

    @staticmethod
    def parse_price(response: Response) -> float:
        return float(response.css(".price_color::text").get().replace("£", ""))

    @staticmethod
    def parse_amount_in_stock(response: Response) -> int:
        return int(
            re.findall(
                r"\d+",
                response.css("table tr:nth-child(6) > td::text").get()
            )[0]
        )

    @staticmethod
    def parse_rating(response: Response) -> int:
        return word_to_num(response.css(".star-rating::attr(class)").get())

    @staticmethod
    def parse_category(response: Response) -> str:
        return response.css(".breadcrumb li:nth-child(3) > a::text").get()

    @staticmethod
    def parse_description(response: Response) -> str:
        return response.css(".sub-header + p::text").get()

    @staticmethod
    def parse_upc(response: Response) -> str:
        return response.css("table tr:first-child > td::text").get()

    def parse_book(self, response: Response) -> None:
        yield {
            "title": self.parse_title(response),
            "price": self.parse_price(response),
            "amount_in_stock": self.parse_amount_in_stock(response),
            "rating": self.parse_rating(response),
            "category": self.parse_category(response),
            "description": self.parse_description(response),
            "upc": self.parse_upc(response),
        }

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            book_link = book.css(".product_pod > h3 > a::attr(href)").get()

            if book_link:
                yield response.follow(book_link, self.parse_book)

        next_page = response.css(".pager > .next > a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

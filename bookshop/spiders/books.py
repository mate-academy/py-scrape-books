import re
from typing import Generator

import scrapy
from scrapy.http import Response


SCORES = {
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

    def parse(self, response: Response, **kwargs) -> Generator[scrapy.Request, None, None]:
        book_links = response.css("article > h3 > a")
        for book_link in book_links:
            yield response.follow(book_link, callback=BooksSpider.parse_book)

        next_page = response.css("ul.pager > li.next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_book(response: Response) -> dict:
        return {
            "title": BooksSpider._get_title(response),
            "price": BooksSpider._get_price(response),
            "amount_in_stock": BooksSpider._get_amount_in_stock(response),
            "rating": BooksSpider._get_rating(response),
            "category": BooksSpider._get_category(response),
            "description": BooksSpider._get_description(response),
            "upc": BooksSpider._get_upc(response),
        }

    @staticmethod
    def _get_title(response: Response) -> str:
        return response.css(".product_main > h1::text").get()

    @staticmethod
    def _get_price(response: Response) -> float:
        return float(response.css(".price_color::text").get().replace("£", ""))

    @staticmethod
    def _get_amount_in_stock(response: Response) -> int:
        info_table = response.css(".table td::text").getall()
        return re.findall(r"\d+", info_table[5])[0]

    @staticmethod
    def _get_rating(response: Response) -> int:
        return SCORES[response.css(
            ".star-rating::attr(class)"
        ).get().split()[1]]

    @staticmethod
    def _get_category(response: Response) -> str:
        return response.css("ul.breadcrumb > li > a::text").getall()[-1]

    @staticmethod
    def _get_description(response: Response) -> str:
        return response.css(".product_page > p::text").get()

    @staticmethod
    def _get_upc(response: Response) -> str:
        info_table = response.css(".table td::text").getall()
        return info_table[0]

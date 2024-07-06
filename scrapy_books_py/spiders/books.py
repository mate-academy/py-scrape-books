from typing import Dict, Any

import scrapy
from scrapy.http import Response

RATING = {
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

    def parse(self, response: Response, **kwargs) -> str:
        for book in response.css("article.product_pod"):
            book_detail_url = response.urljoin(book.css("h3 a::attr(href)").get())
            yield response.follow(book_detail_url, callback=self._parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book(self, response: Response) -> Dict[str, Any]:
        yield {
            "title": self._parse_title(response),
            "price": self._parse_price(response),
            "amount_in_stock": self._parse_amount(response),
            "rating": self._parse_rating(response),
            "category": self._parse_category(response),
            "description": self._parse_description(response),
            "upc": self._parse_upc(response),
        }

    @staticmethod
    def _parse_title(response: Response) -> str:
        return response.css("h1::text").get()

    @staticmethod
    def _parse_price(response: Response) -> float:
        return float(response.css("p.price_color::text").get().replace("£", ""))

    @staticmethod
    def _parse_amount(response: Response) -> int:
        return response.css("p.availability::text").re_first("\d+")

    @staticmethod
    def _parse_rating(response: Response) -> int:
        class_name = response.css("p.star-rating::attr(class)").get().split()[-1]
        return RATING.get(class_name, 0)

    @staticmethod
    def _parse_category(response: Response) -> str:
        return response.css("ul.breadcrumb li a::text").getall()[-1]

    @staticmethod
    def _parse_description(response: Response) -> str:
        return response.css("div#product_description ~ p::text").get()

    @staticmethod
    def _parse_upc(response: Response) -> str:
        return response.css("table.table tr:nth-child(1) td::text").get()

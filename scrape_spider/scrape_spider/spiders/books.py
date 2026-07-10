from scrapy import Spider, Request
from scrapy.http import Response
from typing import Iterator
from scrape_spider.items import BookItem

RATING = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Iterator[Request]:
        for book in response.css(".product_pod h3 a::attr(href)").getall():
            yield response.follow(book, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


    def parse_book(self, response: Response) -> Iterator[BookItem]:
        yield BookItem(**self._parse_book(response))

    def _parse_book(self, response: Response) -> dict:
        return {
            "title": self._parse_title(response),
            "price": self._parse_price(response),
            "amount_in_stock": self._parse_amount_in_stock(response),
            "rating": self._parse_rating(response),
            "category": self._parse_category(response),
            "description": self._parse_description(response),
            "upc": self._parse_upc(response),
        }

    def _parse_title(self, response: Response) -> str:
        return response.css("h1::text").get()

    def _parse_price(self, response: Response) -> float:
        price = response.css(".price_color::text").get()
        return float(price.replace("£", ""))

    def _parse_amount_in_stock(self, response: Response) -> int:
        text = " ".join(
            response.css(".product_main .availability::text").getall()
        )
        digits = "".join(char for char in text if char.isdigit())
        return int(digits) if digits else 0

    def _parse_rating(self, response: Response) -> int:
        rating = response.css("p.star-rating::attr(class)").get()
        word = rating.replace("star-rating", "").strip()
        return RATING.get(word, 0)

    def _parse_category(self, response: Response) -> str:
        return response.css(".breadcrumb li a::text").getall()[-1]

    def _parse_description(self, response: Response) -> str:
        return response.css("#product_description ~ p::text").get(default="")

    def _parse_upc(self, response: Response) -> str:
        return response.css("table tr td::text").get()

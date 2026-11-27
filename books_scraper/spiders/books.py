from typing import Generator

import scrapy
from scrapy.http import Response


RATINGS = {
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

    def parse(self, response: Response, **kwargs) -> Generator:
        yield from response.follow_all(
            css="article.product_pod h3 a",
            callback=self.parse_book,
        )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> Generator:
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": self._get_price(response),
            "amount_in_stock": self._get_amount_in_stock(response),
            "rating": self._get_rating(response),
            "category": response.css(
                ".breadcrumb li:nth-child(3) a::text"
            ).get(),
            "description": response.css(
                "#product_description ~ p::text"
            ).get(),
            "upc": response.css(
                "table tr:nth-child(1) td::text"
            ).get(),
        }

    @staticmethod
    def _get_price(response: Response) -> float:
        price = response.css(".product_main .price_color::text").get()
        return float(price.replace("£", ""))

    @staticmethod
    def _get_amount_in_stock(response: Response) -> int:
        amount = response.css(".product_main .availability").re_first(
            r"\d+"
        )
        return int(amount)

    @staticmethod
    def _get_rating(response: Response) -> int:
        rating_class = response.css(
            ".product_main .star-rating::attr(class)"
        ).get()
        return RATINGS[rating_class.split()[-1]]

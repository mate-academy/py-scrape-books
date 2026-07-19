import re

import scrapy
from scrapy.http import Response

from books_scraper.items import BookItem

RATING_WORDS = {
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

    def parse(self, response: Response, **kwargs: object) -> None:
        for book_url in response.css("article.product_pod h3 a::attr(href)"):
            yield response.follow(book_url.get(), callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> None:
        table_rows = response.css("table.table.table-striped tr")
        upc = table_rows[0].css("td::text").get()
        availability = table_rows[5].css("td::text").get()

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_word = rating_class.split()[-1]

        yield BookItem(
            title=response.css("div.product_main h1::text").get(),
            price=self._parse_price(
                response.css("p.price_color::text").get()
            ),
            amount_in_stock=self._parse_amount_in_stock(availability),
            rating=RATING_WORDS[rating_word],
            category=response.css(
                "ul.breadcrumb li:nth-child(3) a::text"
            ).get(),
            description=response.css(
                "div#product_description + p::text"
            ).get(default=""),
            upc=upc,
        )

    @staticmethod
    def _parse_price(raw_price: str) -> float:
        return float(re.sub(r"[^\d.]", "", raw_price))

    @staticmethod
    def _parse_amount_in_stock(raw_availability: str) -> int:
        match = re.search(r"\d+", raw_availability)
        return int(match.group()) if match else 0

import re
from typing import Iterator

import scrapy
from scrapy.http import Response

from scrape_books.items import BookItem

RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Iterator:
        for href in response.css("article.product_pod h3 a::attr(href)"):
            yield response.follow(href, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _parse_price(raw: str) -> float:
        return float(re.search(r"\d+(?:\.\d+)?", raw).group())

    @staticmethod
    def _parse_stock(raw: str) -> int:
        match = re.search(r"\((\d+) available\)", raw)
        return int(match.group(1)) if match else 0

    @staticmethod
    def _parse_rating(classes: str) -> int:
        word = next((c for c in classes.split() if c in RATINGS), None)
        return RATINGS.get(word, 0)

    def parse_book(self, response: Response) -> Iterator[BookItem]:
        table = {
            row.css("th::text").get(): row.css("td::text").get()
            for row in response.css("table.table-striped tr")
        }
        availability = " ".join(
            response.css("p.availability::text").getall()
        )

        yield BookItem(
            title=response.css("div.product_main h1::text").get(),
            price=self._parse_price(
                response.css("p.price_color::text").get()
            ),
            amount_in_stock=self._parse_stock(availability),
            rating=self._parse_rating(
                response.css("p.star-rating::attr(class)").get()
            ),
            category=response.css(
                "ul.breadcrumb li:nth-child(3) a::text"
            ).get(),
            description=response.xpath(
                "//div[@id='product_description']/following-sibling::p/text()"
            ).get(),
            upc=table.get("UPC"),
        )

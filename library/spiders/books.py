from typing import Generator

import scrapy
from scrapy.http import Response

from library.items import BookItem

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    RATING_MAP = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    def _parse_single_book(self, response: Response) -> BookItem:
        self.logger.debug(f"Parsing book: {response.url}")

        book = BookItem()

        try:
            book["title"] = response.css("div.product_main > h1::text").get()
            book["price"] = float(
                response.css(
                    ".price_color::text"
                ).get().replace("£", "")
            )
            book["amount_in_stock"] = int(
                response.css(
                    "p.instock.availability::text"
                ).getall()[1].split()[2].replace("(", "")
            )
            book["rating"] = self.RATING_MAP[
                response.css(
                    "p.star-rating::attr(class)"
                ).get().split()[1]
            ]
            book["category"] = response.css(
                "ul.breadcrumb > li > a::text"
            ).getall()[2]
            book["description"] = response.css(
                "#product_description ~ p::text"
            ).get()
            book["upc"] = response.css(".table.table-striped td::text").get()
        except Exception as e:
            self.logger.error(f"Error parsing book {response.url}: {e}")

        return book

    def parse(
        self, response: Response, **kwargs
    ) -> Generator[scrapy.http.Request]:
        self.logger.info(f"Parsing page: {response.url}")

        for book in response.css("article.product_pod"):
            book_url = book.css("h3 > a::attr(href)").get()
            yield response.follow(book_url, callback=self._parse_single_book)

        next_page = response.css(".pager li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

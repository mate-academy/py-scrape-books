import re

import scrapy
from scrapy.http import Response

from books_scraper.items import BookItem


RATING_MAPPING = {
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

    def parse(self, response: Response, **kwargs) -> None:
        book_links = response.css("article.product_pod h3 a::attr(href)")
        for book_link in book_links:
            yield response.follow(book_link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> BookItem:
        table_data = {
            row.css("th::text").get(): row.css("td::text").get()
            for row in response.css("table.table.table-striped tr")
        }

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_word = rating_class.split()[-1]

        yield BookItem(
            title=response.css("div.product_main h1::text").get(),
            price=self.parse_price(table_data["Price (excl. tax)"]),
            amount_in_stock=self.parse_amount_in_stock(
                table_data["Availability"]
            ),
            rating=RATING_MAPPING[rating_word],
            category=response.css("ul.breadcrumb li a::text").getall()[-1],
            description=response.css(
                "#product_description + p::text"
            ).get(default=""),
            upc=table_data["UPC"],
        )

    @staticmethod
    def parse_price(price_text: str) -> float:
        return float(price_text.replace("£", ""))

    @staticmethod
    def parse_amount_in_stock(availability_text: str) -> int:
        match = re.search(r"(\d+)\s+available", availability_text)
        return int(match.group(1)) if match else 0

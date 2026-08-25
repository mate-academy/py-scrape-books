import re
from typing import Iterator

import scrapy
from scrapy.http import Response

from book_scraper.items import BookItem

RATING_WORDS = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def extract_number(text: str) -> int:
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0


def extract_price(text: str) -> float:
    return float(re.sub(r"[^\d.]", "", text))


def get_table_data(response: Response) -> dict[str, str]:
    return {
        row.css("th::text").get(): "".join(row.css("td::text").getall())
        for row in response.css("table.table-striped tr")
    }


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(
        self, response: Response, **kwargs: str
    ) -> Iterator[scrapy.Request]:
        book_links = response.css(".product_pod h3 a::attr(href)")
        for link in book_links:
            yield response.follow(link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> BookItem:
        table_data = get_table_data(response)

        rating_class = response.css("p.star-rating::attr(class)").get()
        rating_word = rating_class.split()[-1]

        description = response.css(
            "#product_description ~ p::text"
        ).get(default="")

        category = response.css("ul.breadcrumb li a::text").getall()[-1]

        return BookItem(
            title=response.css("h1::text").get(),
            price=extract_price(table_data["Price (incl. tax)"]),
            amount_in_stock=extract_number(table_data["Availability"]),
            rating=RATING_WORDS[rating_word],
            category=category,
            description=description,
            upc=table_data["UPC"],
        )

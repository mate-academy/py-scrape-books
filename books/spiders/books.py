import re

import scrapy

from books.items import BookItem

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        "https://books.toscrape.com/catalogue/page-1.html",
    ]

    def parse(self, response: scrapy.http.Response) -> scrapy.Request:
        for book_link in response.css(
            "article.product_pod h3 a::attr(href)"
        ).getall():
            yield response.follow(book_link, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: scrapy.http.Response) -> BookItem:
        availability = response.css(
            "p.instock.availability"
        ).xpath("normalize-space()").get() or ""
        stock_match = re.search(r"\((\d+)\s+available\)", availability)

        rating_classes = response.css(
            "p.star-rating::attr(class)"
        ).get() or ""
        rating_word = next(
            (
                word for word in rating_classes.split()
                if word in RATING_MAP
            ),
            None,
        )

        description = response.css(
            "#product_description ~ p::text"
        ).get() or ""

        yield BookItem(
            title=response.css("div.product_main h1::text").get(),
            price=self._normalize_price(
                response.css("p.price_color::text").get() or ""
            ),
            amount_in_stock=(
                int(stock_match.group(1)) if stock_match else 0
            ),
            rating=RATING_MAP.get(rating_word, 0),
            category=response.css(
                "ul.breadcrumb li:nth-child(3) a::text"
            ).get(),
            description=description,
            upc=response.css(
                "table.table.table-striped tr:contains('UPC') "
                "td::text"
            ).get(),
        )

    @staticmethod
    def _normalize_price(raw_price: str) -> str:
        return (
            raw_price.replace("£", "")
            .replace(",", "")
            .strip()
        )

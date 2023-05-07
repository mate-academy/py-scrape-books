import scrapy

from scrapy.http import Response
from dataclasses import dataclass


@dataclass
class Book:
    title: str
    price: float
    amount_in_stock: int
    rating: int
    category: str
    description: str
    upc: str


RATING = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BookSpider(scrapy.Spider):
    name = "books"
    start_urls = [
        "https://books.toscrape.com/"
    ]

    def parse(
            self,
            response: scrapy.http.Response,
            **kwargs
    ) -> scrapy.Request:
        for book in response.css(".product_pod"):
            detail_url = book.css("a::attr(href)").extract_first()
            yield scrapy.Request(
                response.urljoin(detail_url),
                self.parse_book
            )
        next_link = response.css(".next a::attr(href)").get()
        yield scrapy.Request(
            response.urljoin(next_link),
            self.parse
        )

    @staticmethod
    def parse_book(book: Response) -> Book:
        yield Book(
            title=book.css(".product_main > h1::text").get(),
            price=float(
                book.css(".price_color::text").get().replace("£", "")
            ),
            amount_in_stock=int(
                "".join([num for num in book.css(
                    "tr:nth-child(6) > td::text"
                ).get() if num.isdigit()])
            ),
            rating=RATING[
                book.css("p.star-rating::attr(class)").get().split()[-1]
            ],
            category=book.css("li:nth-child(3) a::text").get(),
            description=book.css("article > p::text").get(),
            upc=book.css(".table tr:nth-child(1) td::text").get()
        )

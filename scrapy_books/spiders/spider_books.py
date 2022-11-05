from dataclasses import dataclass

import scrapy
import re


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
    name = "books-scrapy"
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
                self.parse_detail
            )
        next_link = response.css(".next a::attr(href)").get()
        yield scrapy.Request(
            response.urljoin(next_link),
            self.parse
        )

    @staticmethod
    def parse_detail(response: scrapy.http.Response) -> Book:
        yield Book(
            title=response.css(".product_main h1::text").extract_first(),
            price=float(
                response.css(".price_color::text").extract_first()[1:]
            ),
            amount_in_stock=int(
                re.findall(
                    r"\d+", response.css(
                        ".availability::text"
                    ).extract()[1].strip()
                )[0]
            ),
            rating=RATING[
                response.css(".star-rating::attr(class)").get().split()[1]
            ],
            category=response.css(".breadcrumb li a::text").extract()[-1],
            description=response.css(
                "#product_description + p::text"
            ).get().encode("ascii", "ignore").decode(),
            upc=response.css(".table td::text").extract_first()
        )

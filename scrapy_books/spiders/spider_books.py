from dataclasses import dataclass

import scrapy


@dataclass
class Book:
    title: str
    price: float
    amount_in_stock: int
    rating: int
    category: str
    description: str
    upc: str


class BookSpider(scrapy.Spider):
    name = "books-scrapy"
    start_urls = [
        "https://books.toscrape.com/"
    ]

    def parse(self, response, **kwargs):
        for book in response.css(".product_pod"):
            detail_url = book.css("a::attr(href)").extract_first()
            yield scrapy.Request(
                response.urljoin(detail_url),
                self.parse_detail
            )

    @staticmethod
    def parse_detail(response, **kwargs):
        yield Book(
            title=response.css(".product_main h1::text").extract_first(),
            price=float(response.css(".price_color::text").extract_first()[1:]),
            amount_in_stock=int("123"),
            #     response.css(".instock::text").extract_first()[11:12]
            # ),
            rating=response.css(".star-rating::attr(class)").get().split()[1],
            category="123",
            description=response.css("#product_description + p::text").get(),
            upc=response.css(".table td::text").extract_first()
        )

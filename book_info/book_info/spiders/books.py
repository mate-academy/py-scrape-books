from typing import Generator, Any

import scrapy
from scrapy.http import Response
from word2number import w2n


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> Generator[dict[Any]:
        for book in response.css(".product_pod"):
            detail_page = book.css("h3 a::attr(href)").get()
            yield response.follow(detail_page, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_book(response: Response) -> Generator[dict[Any]:
        title = response.css("h1::text").get()
        price = float(
            response.css("p.price_color::text").get().replace("£", "")
        )
        amount_in_stock = int(
            "".join(
                [
                    char
                    for char in response.css(
                        "th:contains('Availability') + td::text"
                    ).get()
                    if char.isdigit()
                ]
            )
        )
        rating = w2n.word_to_num(
            response.css("p.star-rating::attr(class)").get().split()[1]
        )
        category = response.css("th:contains('Product Type') + td::text").get()
        description = response.css("#product_description + p").get()[3:-4]
        upc = response.css("th:contains('UPC') + td::text").get()

        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }

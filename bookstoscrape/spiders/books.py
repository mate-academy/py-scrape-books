from pathlib import Path

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    def parse_book_details(self, response: Response) -> None:
        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "amount_in_stock": response.css(
                "tr:contains('Availability') td::text"
            ).re_first(r"\d+"),
            "rating": self.rating_map.get(
                response.css(".star-rating::attr(class)").get().split()[-1], 0
            ),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": response.css("tr:contains('UPC') td::text").get(),
        }

    def parse(self, response: Response, **kwargs) -> None:
        filename = "bookss.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

        for book in response.css("div.image_container a"):
            book_url = response.urljoin(book.css("::attr(href)").get())
            yield response.follow(book_url, callback=self.parse_book_details)

        next_page = response.css("a:contains('next')::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

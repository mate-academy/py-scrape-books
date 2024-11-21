from pathlib import Path

import scrapy

from scrapy.http import Response
from scrapy.selector import Selector
from selenium import webdriver
from twisted.internet.defer import Deferred


def extract_star_rating(class_name: str) -> int:
    star_mapping = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    rating_verb = class_name.split()[-1]

    if rating_verb in star_mapping:
        return star_mapping[rating_verb]

    return 0


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str) -> Deferred[None] | None:
        self.driver.close()
        return self.close(reason)

    def _parse_detail_page(self, book: Selector, response: Response) -> dict:
        detail_page = book.css("a::attr(href)").get()
        detail_page = response.urljoin(detail_page)
        self.driver.get(detail_page)
        html = self.driver.page_source
        detail_selector = Selector(text=html)

        return {
            "category": detail_selector.css(
                ".breadcrumb > li a::text"
            ).getall()[2],
            "description": detail_selector.css(
                ".product_page > p::text"
            ).get(),
            "upc": detail_selector.css(".table-striped td::text").get(),
            "amount_in_stock": detail_selector.css(
                "p.instock.availability::text"
            ).re_first(r"\((\d+)\s")
        }

    def parse(self, response: Response, *args, **kwargs) -> None:
        filename = "products.html"
        Path(filename).write_bytes(response.body)
        self.log("Saved file {filename}")
        for book in response.css(".product_pod"):
            book_data = {
                "title": book.css("a::attr(title)").get(),
                "price": float(
                    book.css(".price_color::text").get().replace("£", "")
                ),
                "rating": extract_star_rating(
                    book.css(".star-rating::attr(class)").get()
                ),
            }

            details = self._parse_detail_page(book=book, response=response)

            yield {**book_data, **details}

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

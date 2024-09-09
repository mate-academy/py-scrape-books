import scrapy
from scrapy.http import Response
from selenium import webdriver
from typing import Any, Generator
from books.items import BooksItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    text_to_number = {
        "Zero": 0,
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: any) -> None:
        self.driver.close()

    def parse(
            self, response: Response, **kwargs: Any
    ) -> Generator[scrapy.Request, None, None]:
        for book in response.css(".product_pod"):
            detail_url = book.css("h3 > a::attr(href)").get()
            yield response.follow(detail_url, callback=self.parse_book_info)

    def parse_book_info(
            self, response: Response
    ) -> Generator[BooksItem]:
        yield {
            "title": response.css(
                ".product_main > h1::text"
            ).get(),
            "price": response.css(
                ".product_main > .price_color::text"
            ).get().replace("£", ""),
            "amount_in_stock": response.css(
                ".product_main > p.availability::text"
            ).re_first(r"\d+"),
            "rating": BooksSpider.text_to_number.get(
                response.css("p.star-rating::attr(class)").get().split()[1], 0
            ),
            "category": response.css(
                ".breadcrumb > li > a::text"
            ).getall()[-1],
            "description": response.css(
                "#product_description ~ p::text"
            ).get(),
            "upc": response.css("tr > td::text").get(),
        }

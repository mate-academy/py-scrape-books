from typing import Generator

import scrapy
from scrapy import Spider
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from twisted.internet.defer import Deferred

numbers = {
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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()

    def close(self: Spider, reason: str) -> Deferred[None] | None:
        self.driver.close()
        return self.close(reason)

    def parse(self, response: Response) -> Generator:
        for book in response.css(".product_pod"):
            absolute_url = response.urljoin(book.css("a::attr(href)").get())
            self.driver.get(absolute_url)
            yield {
                "title": book.css("a::attr(title)").get(),
                "price": float(book.css(".price_color::text").get()[1:]),
                "amount_in_stock": self._get_book_amount_in_stock(),
                "rating": numbers[
                    book.css(".star-rating::attr(class)").get().split()[1]
                ],
                "category": self._get_book_category(),
                "description": self._get_book_description(),
                "upc": self._get_book_upc(),
            }

        next_page = response.css(".pager .next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _get_book_amount_in_stock(self) -> int:
        amount_in_stock = (
            self.driver
            .find_element(By.CLASS_NAME, "instock")
            .text.split()
        )[2][1:]
        return int(amount_in_stock)

    def _get_book_category(self) -> str:
        category = (
            self.driver
            .find_element(By.CLASS_NAME, "breadcrumb")
            .find_elements(By.TAG_NAME, "a")[2]
            .text
        )
        return category

    def _get_book_description(self) -> str:
        description = (
            self.driver
            .find_element(By.ID, "product_description")
            .find_element(By.XPATH, "./following-sibling::p[1]")
            .text
        )
        return description

    def _get_book_upc(self) -> str:
        upc = (
            self.driver
            .find_element(By.CLASS_NAME, "table")
            .find_element(By.XPATH, ".//td")
            .text
        )
        return upc

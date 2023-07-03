from typing import Any
from urllib.parse import urljoin

import scrapy
from selenium import webdriver
from scrapy.http import Response
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

STAR_RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: Any) -> None:
        self.driver.close()

    def parse(self, response: Response, **kwargs) -> dict | Response:
        for book in response.css(".product_pod"):
            detailed_page_url = book.css("h3 > a::attr(href)").get()
            amount, category, description, upc = self._parse_detailed_page(
                detailed_page_url, response
            )
            yield {
                "title": book.css("h3 > a::attr(title)").get(),
                "price": float(book.css(".price_color::text").get()[1:]),
                "amount_in_stock": amount,
                "rating": STAR_RATING_MAP.get(
                    book.css(".star-rating::attr(class)").get().split()[-1]
                ),
                "category": category,
                "description": description,
                "upc": upc,
            }

            next_page = response.css("li.next a::attr(href)").get()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def _parse_detailed_page(self, url: str, response: Response) -> list[int | str]:
        self.driver.get(urljoin(response.url, url))
        amount_in_stock = 0
        category = ""
        upc = ""
        description = ""

        try:
            amount_in_stock = int(
                self.driver.find_element(By.CLASS_NAME, "instock")
                .text.replace("In stock (", "")
                .split()[0]
            )
        except NoSuchElementException:
            pass

        try:
            category = self.driver.find_element(
                By.CSS_SELECTOR, "ul.breadcrumb > li:nth-child(3) > a"
            ).text
        except NoSuchElementException:
            pass

        try:
            upc = self.driver.find_element(By.TAG_NAME, "td").text
        except NoSuchElementException:
            pass

        description_block = self.driver.find_elements(
            By.CSS_SELECTOR, "div > article > p"
        )

        if description_block:
            description = description_block[0].text
        return amount_in_stock, category, description, upc

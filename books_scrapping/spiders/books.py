from typing import Generator

import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By

RATING_STR_TO_INT = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    start_urls = ["https://books.toscrape.com"]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def _parse_detail_page(self, response: Response, book: Selector) -> dict:
        detailed_url = response.urljoin(book.css("h3 a::attr(href)").get())
        self.driver.get(detailed_url)
        main = self.driver.find_element(By.CLASS_NAME, "product_main")
        title = main.find_element(By.TAG_NAME, "h1").text
        price = float(main.find_element(By.CLASS_NAME, "price_color").text[1:])
        amount_in_stock = int(
            main.find_element(By.CLASS_NAME, "instock").text.split()[-2][1:]
        )
        rating = RATING_STR_TO_INT[
            main.find_element(By.CLASS_NAME, "star-rating")
            .get_attribute("class")
            .split()[-1]
        ]
        breadcrumb = self.driver.find_element(By.CLASS_NAME, "breadcrumb")
        category = breadcrumb.find_elements(By.CSS_SELECTOR, "li a")[-1].text
        description = (
            self.driver.find_element(By.CLASS_NAME, "product_page")
            .find_elements(By.TAG_NAME, "p")[-1]
            .text
        )
        upc = (
            self.driver.find_element(By.CLASS_NAME, "table")
            .find_element(By.TAG_NAME, "tr")
            .find_element(By.TAG_NAME, "td")
            .text
        )

        return {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }

    def parse(self, response, **kwargs) -> Generator[dict, None, None]:
        for book in response.css("article.product_pod"):
            yield self._parse_detail_page(response, book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

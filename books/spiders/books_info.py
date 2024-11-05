from typing import Any
import re

import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BooksInfoSpider(scrapy.Spider):
    name = "books_info"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

    def close(self, reason) -> None:
        self.driver.close()

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            yield self.parse_detail_page(response, book)

        next_page = response.css(".pager > .next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def _get_num_available_books(self, text: str) -> int:
        match = re.search(r'\((\d+) available\)', text)
        if match:
            return int(match.group(1))
        return 0

    def parse_detail_page(self, response: Response, book: Selector) -> dict[str, Any]:
        detailed_url = response.urljoin(book.css("h3 > a::attr(href)").get())
        self.driver.get(detailed_url)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".breadcrumb"))
        )

        page_source = self.driver.page_source
        detail_response = Selector(text=page_source)

        return {
            "title": detail_response.css(".product_main > h1::text").get(),
            "price": float(detail_response.css(".price_color::text").get().replace("£", "")),
            "amount_in_stock": self._get_num_available_books(detail_response.css("tr")[-2].css("td::text").get()),
            "rating": detail_response.css(".star-rating::attr(class)").get().split()[-1],
            "category": detail_response.css(".breadcrumb > li")[-2].css("a::text").get(),
            "description": detail_response.css("#product_description + p::text").get(),
            "upc": detail_response.css("td::text").get(),
        }

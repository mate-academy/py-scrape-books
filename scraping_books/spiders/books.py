import scrapy
from scrapy.http import Response
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from twisted.internet.defer import Deferred
from typing_extensions import Any


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str) -> Deferred:
        self.driver.quit()
        return super().close(reason)

    def parse(self, response: Response, **kwargs) -> None:
        for product in response.css(".product_pod"):
            book_url = product.css("h3 a::attr(href)").get()
            book_data = self._parse_inner_data(response.urljoin(book_url))

            yield {
                "title": product.css("h3 a::attr(title)").get(),
                "price": product.css(".price_color::text").get(),
                "amount_in_stock": book_data.get("amount_in_stock"),
                "rating": product.css("p.star-rating::attr(class)").re_first(
                    r"star-rating (\w+)"
                ),
                "category": book_data.get("category"),
                "description": book_data.get("description"),
                "upc": book_data.get("upc"),
            }

        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        else:
            print("No next page found.")

    def _parse_inner_data(self, book_url: str) -> dict[str, Any]:
        self.driver.get(book_url)

        try:
            stock_availability = (
                WebDriverWait(self.driver, 10)
                .until(
                    ec.visibility_of_element_located(
                        (By.CSS_SELECTOR, ".instock.availability")
                    )
                )
                .text.strip()
            )
        except NoSuchElementException:
            stock_availability = None

        try:
            category_in_page = (
                WebDriverWait(self.driver, 10)
                .until(
                    ec.visibility_of_element_located(
                        (By.CSS_SELECTOR, ".breadcrumb li:nth-child(3) a")
                    )
                )
                .text.strip()
            )
        except NoSuchElementException:
            category_in_page = None

        try:
            description = self.driver.find_element(
                By.CSS_SELECTOR, "#product_description ~ p"
            ).text
        except NoSuchElementException:
            description = None

        try:
            upc = self.driver.find_element(
                By.XPATH, "//th[text()='UPC']/following-sibling::td"
            ).text
        except NoSuchElementException:
            upc = None

        return {
            "amount_in_stock": stock_availability,
            "category": category_in_page,
            "description": description,
            "upc": upc,
        }

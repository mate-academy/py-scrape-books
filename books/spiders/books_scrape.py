from typing import Any

import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


class BooksScrapeSpider(scrapy.Spider):
    name = "books_scrape"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.driver = self.get_headless_driver()

    def get_headless_driver(self) -> WebDriver:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        return driver

    def close(self, reason: str) -> None:
        self.driver.quit()

    @staticmethod
    def rating_convert(number_str: str) -> int:
        conversion_dict = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        return conversion_dict.get(number_str, 0)

    def parse(self, response: Response, **kwargs: Any) -> dict[str, Any]:
        for book in response.css(".product_pod"):
            book_detail_info = self._parse_book_detail_info(response, book)

            yield {
                "title": book.css("a[href]::attr(title)").get(),
                "price": float(
                    book.css(".price_color::text").re_first(r"\d+\.\d+")
                ),
                "rating": self.rating_convert(
                    book.css("p.star-rating::attr(class)")
                    .extract_first().split()[-1]
                ),
                **book_detail_info,
            }

        next_page = response.css(".pager > li.next > a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book_detail_info(
        self, response: Response, book: Selector
    ) -> dict[str, Any]:
        detail_url = response.urljoin(book.css("h3 > a::attr(href)").get())
        self.driver.get(detail_url)

        in_stock = (
            self.driver.find_element(By.CLASS_NAME, "product_main")
            .find_element(By.CLASS_NAME, "instock")
            .text
        )
        amount_in_stock = int("".join(filter(str.isdigit, in_stock)))

        category = (
            self.driver.find_element(By.CLASS_NAME, "breadcrumb")
            .find_elements(By.TAG_NAME, "li")[-2]
            .text
        )

        try:
            description = self.driver.find_element(
                By.CSS_SELECTOR, "article.product_page > p"
            ).text
        except NoSuchElementException:
            description = "No description"

        product_information = self.driver.find_element(
            By.CLASS_NAME, "table-striped"
        )
        upc_value = product_information.find_element(
            By.XPATH, "//th[text()='UPC']/following-sibling::td"
        ).text

        return {
            "amount_in_stock": amount_in_stock,
            "category": category,
            "description": description,
            "upc": upc_value,
        }

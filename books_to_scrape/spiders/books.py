import random
from typing import Any

import scrapy
from scrapy import Selector, Request
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from twisted.internet.asyncioreactor import AsyncioSelectorReactor

reactor = AsyncioSelectorReactor
reactor._handleSignals = lambda x: 0


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.driver = self._get_webdriver()

    def close(self, reason: Any) -> None:
        self.driver.close()

    def parse(self, response: Response, **kwargs) -> Request:
        for book in response.css("article.product_pod"):
            yield self._parse_book_detail_info(response, book)

        next_page = response.css(".next > a::attr(href)").get()

        self.driver.close()

        self.driver = self._get_webdriver()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book_detail_info(
            self,
            response: Response,
            book: Selector
    ) -> dict[str]:

        book_detail_url = response.urljoin(
            book.css("h3 > a::attr(href)").get()
        )

        self.driver.get(book_detail_url)

        title = self.driver.find_element(
            By.CSS_SELECTOR,
            "div.col-sm-6.product_main > h1"
        ).text
        price = float(self.driver.find_element(
            By.CLASS_NAME, "price_color"
        ).text.replace("£", ""))
        amount_in_stock = int(self.driver.find_element(
            By.CSS_SELECTOR, ".instock.availability"
        ).text.split()[2][1:])
        rating = self._get_rating(
            self.driver.find_element(
                By.CLASS_NAME, "star-rating"
            )
        )
        category = self.driver.find_elements(
            By.CSS_SELECTOR, ".breadcrumb > li"
        )[2].text
        description = self._get_description(
            self.driver.find_elements(
                By.CSS_SELECTOR, "#content_inner > article > p"
            )
        )
        upc = self.driver.find_element(
            By.CSS_SELECTOR,
            ".table.table-striped > tbody > tr:nth-child(1) > td"
        ).text

        return {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }

    def _get_webdriver(self) -> WebDriver:
        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_argument("--headless")
        chrome_options.add_argument(
            f"user-agent={self._get_random_user_agent()}"
        )

        return webdriver.Chrome(options=chrome_options)

    def _get_random_user_agent(self) -> str:
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",

            "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/51.0.2704.64 Safari/537.36",

            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) "
            "AppleWebKit/601.3.9 (KHTML, like Gecko) "
            "Version/9.0.2 Safari/601.3.9",

            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) "
            "Gecko/20100101 Firefox/15.0.1",

            "Mozilla/5.0 "
            "(Linux; Android 12; SM-X906C Build/QP1A.190711.020; wv) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Version/4.0 Chrome/80.0.3987.119 "
            "Mobile Safari/537.36",

            "Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) "
            "AppleWebKit/602.1.50 (KHTML, like Gecko) "
            "Version/10.0 Mobile/19A346 Safari/602.1",

            "Mozilla/5.0 "
            "(iPhone13,2; U; CPU iPhone OS 14_0 like Mac OS X) "
            "AppleWebKit/602.1.50 (KHTML, like Gecko) "
            "Version/10.0 Mobile/15E148 Safari/602.1",
        ]
        return random.choice(user_agents)

    def _get_rating(self, element: WebElement) -> int:
        rating_dict = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        return rating_dict[
            element.get_attribute("class").split()[-1]
        ]

    def _get_description(self, elements: list[WebElement]) -> str:
        if elements:
            return elements[0].text
        else:
            return "No description"

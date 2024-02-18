from dataclasses import dataclass
from typing import Any

import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

mapping_number_rating = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


@dataclass
class Book:
    title: str
    price: float
    amount_in_stock: int
    rating: int
    category: str
    description: str
    upc: int


class BooksScrapeSpider(scrapy.Spider):
    name = "books_scrape"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str) -> None:
        self.driver.close()

    def parse(self, response: Response, **kwargs):
        books = response.css("article.product_pod")
        for book in books:
            yield self._parse_book_detail(response, book)

        next_page = response.css(".pager > li")[-1].css("a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book_detail(self, response: Response, book: Selector):
        detail_url = response.urljoin(book.css("a::attr(href)").get())
        self.driver.get(detail_url)

        rating_element = self.driver.find_element(By.CSS_SELECTOR, "p.star-rating")
        class_attribute = rating_element.get_attribute("class")
        rating_text = class_attribute.split()[-1]
        rating_number = mapping_number_rating.get(rating_text)

        breadcrumb = self.driver.find_element(By.CLASS_NAME, "breadcrumb")
        list_items = breadcrumb.find_elements(By.TAG_NAME, "li")
        category = list_items[2].text.strip()

        try:
            description_element = self.driver.find_element(By.ID, "product_description")
            description = description_element.find_element(
                By.XPATH, "./following-sibling::p[1]"
            ).text
        except NoSuchElementException:
            description = "Description was not found"

        tr_rows = self.driver.find_elements(By.CSS_SELECTOR, "tr")
        td_upc = tr_rows[0].find_element(By.CSS_SELECTOR, "td").text

        return {
            "title": self.driver.find_element(By.TAG_NAME, "h1").text,
            "price": float(
                self.driver.find_element(By.CLASS_NAME, "price_color").text.replace(
                    "£", ""
                )
            ),
            "amount_in_stock": int(
                self.driver.find_element(By.CLASS_NAME, "instock")
                .text.split()[2]
                .replace("(", "")
            ),
            "rating": rating_number,
            "category": category,
            "description": description,
            "upc": td_upc,
        }

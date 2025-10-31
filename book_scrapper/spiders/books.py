from typing import Any

import scrapy
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from twisted.internet.defer import Deferred

STARS_MAP = {
    "Zero": 0,
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Edge()

    def close(self, reason: str) -> Deferred[None] | None:
        self.driver.quit()
        return super().close(self, reason)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        for book in response.css("article.product_pod"):
            yield self._parse_book_info(response, book)

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book_info(self, response: Response, book) -> dict[str, Any]:
        url = response.urljoin(book.css("a::attr(href)").get())
        self.driver.get(url)

        title = self.driver.find_element(By.CSS_SELECTOR, "div.product_main > h1").text
        price_text = self.driver.find_element(By.CSS_SELECTOR, "p.price_color").text[1:]
        in_stock_text = self.driver.find_element(By.CSS_SELECTOR, "p.instock.availability").text
        rating_class = self.driver.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class")
        category_element = self.driver.find_element(By.CSS_SELECTOR, "ul.breadcrumb")
        category = category_element.find_elements(By.CSS_SELECTOR, "li")[2].text
        description = self.driver.find_element(By.CSS_SELECTOR, "article > p").text
        table = self.driver.find_element(By.CSS_SELECTOR, "table.table-striped")
        upc = table.find_element(By.CSS_SELECTOR, "tbody > tr > td").text

        return {
            "title": title,
            "price": float(price_text),
            "amount_in_stock": int(in_stock_text.split()[-2][1:]),
            "rating": STARS_MAP.get(rating_class.split()[-1]),
            "category": category,
            "description": description,
            "upc": upc,
        }

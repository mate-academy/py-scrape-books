import json
from typing import AsyncIterator, Any

import scrapy
from scrapy import Spider
from scrapy.http import Response
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from twisted.internet.defer import Deferred

rating_dict = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5
}


class BooksSpider(scrapy.Spider):
    name = "books"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.options = Options()
        self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options)
        self.catalogue_url = "https://books.toscrape.com/catalogue/"

    def close(self, spider: Spider, reason: str) -> Deferred[None] | None:
        self.driver.close()
        return super().close(spider=spider, reason=reason)

    async def start(self) -> AsyncIterator[Any]:
        for page_num in range(1, 51):
            full_url = f"{self.catalogue_url}page-{page_num}.html"
            yield scrapy.Request(url=full_url, callback=self.parse)

    def parse_single_page(self, url: str) -> dict:
        self.driver.get(url=url)
        amount_in_stock = self.driver.find_element(
            By.CLASS_NAME, "instock"
        ).text
        amount_formatted = amount_in_stock.replace("(", "").split()[2]
        category = self.driver.find_elements(
            By.CSS_SELECTOR, ".breadcrumb > li"
        )[2].text
        upc = self.driver.find_elements(By.CSS_SELECTOR, "td")[0].text
        description = "description"
        try:
            description = (
                self.driver
                .find_element(By.ID, "content_inner")
                .find_element(By.CSS_SELECTOR, ".product_page > p")
                .text
            )
        except NoSuchElementException:
            pass

        return {
            "amount_in_stock": amount_formatted,
            "description": description,
            "category": category,
            "upc": upc
        }

    def write_jl_file(self, record: dict) -> None:
        with open("books.jl", "a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def parse(self, response: Response, **kwargs: Any) -> Any:
        products_pod_css = response.css(".product_pod")
        for product in products_pod_css:
            title = product.css("a::attr(title)").get()
            price_unformatted = product.css(".price_color::text").get()
            price = price_unformatted.replace("£", "")
            rating_unformatted = product.css(".star-rating::attr(class)").get()
            rating = rating_dict.get(rating_unformatted.split(" ")[-1].lower())
            detail_url = (f"{self.catalogue_url}"
                          f"{product.css("a::attr(href)").get()}")
            detail_info = self.parse_single_page(detail_url)
            result = {
                "title": title,
                "price": price,
                "rating": rating,
            }
            result.update(detail_info)
            self.write_jl_file(result)

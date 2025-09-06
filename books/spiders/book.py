import re
from typing import Union
import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from twisted.internet.defer import Deferred


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str) -> Union[Deferred, None]:
        self.driver.close()
        return self.close(reason)

    def parse(self, response: Response, **kwargs) -> Union[Deferred, None]:
        for book in response.css("ol.row > li"):
            yield self.parse_detail_page(response, book)

        next_page = response.css(".pager > li")[-1].css("a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_detail_page(
            self,
            response: Response,
            book: Selector
    ) -> dict:
        absolute_url = response.urljoin(book.css("h3 a::attr(href)").get())
        self.driver.get(absolute_url)

        title = self.driver.find_element(By.CSS_SELECTOR, ".product_main h1").text
        price = float(self.driver.find_element(By.CSS_SELECTOR, ".price_color").text.replace("£", "").strip())
        amount_in_stock = int(
            re.search(r'\d+', self.driver.find_element(By.CSS_SELECTOR, ".product_main .availability").text).group())
        description = self.driver.find_element(
            By.XPATH, "//article[@class='product_page']/p[normalize-space()]"
        ).text
        upc = self.driver.find_element(By.CSS_SELECTOR, "tr td").text
        category = self.driver.find_elements(By.CSS_SELECTOR, ".breadcrumb > li a")[-1].text
        rating_element = self.driver.find_element(By.CSS_SELECTOR, ".product_main .star-rating")
        rating_text = (rating_element
                       .get_attribute("class")
                       .replace("star-rating", "").strip())
        rating_text_to_number = {"One": 1,
                                 "Two": 2,
                                 "Three": 3,
                                 "Four": 4,
                                 "Five": 5}
        rating = rating_text_to_number.get(rating_text, 0)

        return {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "category": category,
            "rating": rating,
            "description": description,
            "upc": upc,
        }

from urllib.parse import urljoin

import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["https://books.toscrape.com/"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=self.options)

    def close(self, reason: str) -> None:
        self.driver.quit()

    def parse(self, response: Response, **kwargs) -> dict:
        for product in response.css(".row > li"):
            page_product = self.parse_page_product(
                product=product
            )
            result = {
                "title": product.css("h3 > a::attr(title)").get(),
                "price": float(
                    product.css(".price_color::text").get().replace("£", "")
                )
            }
            result.update(page_product)

            yield result

        # next_url_page = response.css(".next > a::attr(href)").get()
        # if next_url_page is not None:
        #     yield response.follow(next_url_page, callback=self.parse)

    def get_elem_or_false(self, by: By, value: str) -> WebElement | bool:
        try:
            elem = self.driver.find_element(by, value)
            return elem
        except NoSuchElementException:
            return False

    def parse_page_product(
            self,
            product: Selector
    ) -> dict:
        absolute_url = urljoin(self.allowed_domains[0],
            product.css("h3 > a::attr(href)").get()
        )
        rating_dict = {
            "Zero": 0, "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
        }
        self.driver.get(absolute_url)
        amount_in_stock = int(self.driver.find_element(
            By.CLASS_NAME, "instock"
        ).text.split()[2].replace("(", ""))
        description = self.get_elem_or_false(
            by=By.CLASS_NAME, value="sub-header + p"
        )
        category = self.driver.find_elements(
            By.CLASS_NAME, "breadcrumb > li > a"
        )[-1].text
        rating = self.driver.find_element(
            By.CLASS_NAME, "star-rating"
        ).get_attribute("class").split()[1]
        upc = self.driver.find_elements(
            By.CLASS_NAME, "table-striped > tbody > tr > td"
        )[0].text
        return {
            "amount_in_stock": amount_in_stock,
            "rating": rating_dict[rating],
            "category": category,
            "description": description.text if description else None,
            "upc": upc
        }

import scrapy
from scrapy.http import Response
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str) -> None:
        self.driver.close()

    def parse(self, response: Response, **kwargs) -> dict:
        for book in response.css(".product_pod"):
            detailed_url = response.urljoin(
                book.css("div.image_container a::attr(href)").get()
            )
            self.driver.get(detailed_url)

            try:
                description = self.driver.find_element(
                    By.CSS_SELECTOR, "article.product_page > p"
                ).text
            except NoSuchElementException:
                description = ""

            yield {
                "title": self.driver.find_element(
                    By.CSS_SELECTOR, "div.col-sm-6.product_main > h1"
                ).text,
                "price": self.driver.find_element(
                    By.CLASS_NAME, "price_color"
                ).text.replace("£", ""),
                "amount_in_stock": self.driver.find_element(
                    By.CLASS_NAME, "instock"
                )
                .text.replace("(", "")
                .split()[-2],
                "rating": self.driver.find_element(
                    By.CSS_SELECTOR, "p.star-rating"
                )
                .get_attribute("class")
                .split()[-1],
                "category": self.driver.find_element(
                    By.CSS_SELECTOR, "ul.breadcrumb > li:nth-child(3)"
                ).text,
                "description": description,
                "upc": self.driver.find_element(
                    By.CSS_SELECTOR, "table > tbody > tr:nth-child(1) > td"
                ).text,
            }

        try:
            next_page = response.css("li.next").css("a::attr(href)").get()
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)
        except NoSuchElementException:
            pass

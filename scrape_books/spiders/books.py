import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By

word_to_number = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        "https://books.toscrape.com/"
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason):
        self.driver.close()

    def parse(self, response: Response, **kwargs):
        for book in response.css("article.product_pod"):
            additional_info = self._parse_additional_info(response, book)

            yield {
                "title": book.css("h3 a::attr(title)").get(),
                "price": book.css(".price_color::text").get(),
                "amount_in_stock": additional_info["amount_in_stock"],
                "rating": word_to_number[
                    book.css("p::attr(class)")
                    .get()
                    .split()[1]
                ],
                "category": additional_info["category"],
                "description": additional_info["description"],
                "upc": additional_info["upc"],
            }

        next_page = response.css(".pager .next a::attr(href)").get()

        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def _parse_additional_info(self, response: Response, product: Selector) -> dict:
        detailed_url = response.urljoin(product.css("h3 a::attr(href)").get())
        self.driver.get(detailed_url)

        additional_info = {
            "amount_in_stock": self.driver.find_element(
                By.CSS_SELECTOR, ".product_main .availability"
            ).text.split()[2][1:],
            "category": self.driver.find_elements(
                By.CSS_SELECTOR, ".breadcrumb li"
            )[2].find_element(By.CSS_SELECTOR, "a").text,
            "description": self.driver.find_elements(
                By.CSS_SELECTOR, "article p"
            )[3].text,
            "upc": self.driver.find_element(
                By.CSS_SELECTOR, "table tr td"
            ).text,
        }

        return additional_info


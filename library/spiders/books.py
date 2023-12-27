import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str):
        self.driver.close()

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            detail = self._parse_detail_info(response, book)

            yield {
                "title": book.css(".thumbnail::attr(alt)").get(),
                "price": float(book.css(".price_color::text").get()[1:]),
                "amount_in_stock": detail["amount_in_stock"],
                "rating": self._string_into_int(
                    book.css("p::attr(class)").get().split()[1]
                ),
                "category": detail["category"],
                "description": detail["description"],
                "upc": detail["upc"],
            }

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def _string_into_int(string: str):
        rating = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        return rating[string]

    def _parse_detail_info(self, response: Response, book: Selector):
        detail_book = response.urljoin(
            book.css(".image_container a::attr(href)").get()
        )
        self.driver.get(detail_book)

        try:
            desc = self.driver.find_element(
                By.CSS_SELECTOR, ".product_page > p"
            ).text
        except Exception:
            desc = None
        return {
            "amount_in_stock": int(
                self.driver.find_element(
                    By.CLASS_NAME, "availability"
                ).text.split(" ")[2][1:]
            ),
            "category": self.driver.find_elements(By.TAG_NAME, "li")[2].text,
            "description": desc,
            "upc": self.driver.find_elements(By.TAG_NAME, "td")[0].text,
        }

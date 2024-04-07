import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self) -> None:
        super(BooksSpider, self).__init__()
        self.options = Options()
        self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.options)
        self.NUMBERS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            yield {
                "title": book.css("h3 > a::attr(title)").get(),
                "rating": self.NUMBERS[
                    book.css("p::attr(class)").get().split()[1]
                ],
                "price": float(
                    book.css(".product_price > p::text").get().strip("£")
                ),
                **self._parse_book_details(response, book=book),
            }
        next_page = response.css(".next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def _parse_book_details(self, response: Response, book: Selector) -> dict:
        detail_page = response.urljoin(
            book.css(".image_container > a::attr(href)").get()
        )
        self.driver.get(detail_page)

        return {
            "amount_in_stock": int(
                self.driver.find_elements(
                    By.TAG_NAME, "td"
                )[5].text.split()[2][1:]
            ),
            "category": self.driver.find_elements(
                By.CSS_SELECTOR, ".breadcrumb > li > a"
            )[2].text,
            "description": self.driver.find_element(
                By.CSS_SELECTOR, "#product_description + p"
            ).text,
            "upc": self.driver.find_elements(By.TAG_NAME, "td")[0].text,
        }

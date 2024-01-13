import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


class BooksInfoSpider(scrapy.Spider):
    name = "books_info"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()

    def closed(self, reason: None) -> None:
        self.driver.close()

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod"):
            detailed_info = self._parse_book_details(response, book)
            yield detailed_info

        next_page = response.css(".next > a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book_details(self, response: Response, book: Selector) -> dict:
        detailed_url = response.urljoin(book.css("h3 > a::attr(href)").get())
        self.driver.get(detailed_url)

        return {
            "title": self.get_element_text(".product_main > h1"),
            "price": self.get_element_text(".price_color"),
            "amount_in_stock": int(
                self.get_element_text(".instock.availability")
                .split()[2].strip("(")
            ),
            "rating": int(
                self._parse_rating(
                    book.css(".star-rating::attr(class)").get().split()[1]
                )
            ),
            "category": self.get_element_text(
                ".breadcrumb > li:nth-child(3) > a"
            ),
            "description": self.get_element_text("#product_description + p"),
            "upc": self.get_element_text(
                ".table.table-striped > tbody > tr:nth-child(1) > td"
            ),
        }

    def get_element_text(self, css_selector: str) -> str:
        try:
            return self.driver.find_element(By.CSS_SELECTOR, css_selector).text
        except NoSuchElementException:
            return ""

    @staticmethod
    def _parse_rating(rating: str) -> int:
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        return rating_map[rating]

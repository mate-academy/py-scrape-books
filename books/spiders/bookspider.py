import scrapy
from scrapy.http import Response
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self):
        super().__init__()

        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

    @staticmethod
    def translate_rating(word: str) -> int:
        return {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5
        }.get(word.lower(), 0)

    def safe_find_description(self) -> str | None:
        try:
            return self.driver.find_element(
                By.CSS_SELECTOR, ".product_page > p"
            ).text
        except NoSuchElementException:
            return None

    def close(self, reason):
        self.driver.close()

    def get_detail_info(self, response: Response, book) -> dict:
        detail_page = book.css("h3 > a::attr(href)").get()
        self.driver.get(response.urljoin(detail_page))
        return {
            "amount_in_stock": int(
                self.driver.find_element(
                    By.CSS_SELECTOR, "p.instock.availability"
                ).text.split("(")[1].split()[0]
            ),
            "rating": self.translate_rating(
                self.driver.find_element(
                    By.CSS_SELECTOR, "p.star-rating"
                ).get_attribute("class").split()[1]
            ),
            "category": self.driver.find_elements(
                By.CSS_SELECTOR, "ul.breadcrumb > li"
            )[-2].text,
            "description": self.safe_find_description(),
            "upc": self.driver.find_element(
                By.CSS_SELECTOR, "td"
            ).text
        }

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_data = {
                "title": book.css("h3 > a::attr(title)").get(),
                "price": float(
                    book.css(".price_color::text").get().replace("£", "")
                )
            }
            book_data.update(self.get_detail_info(response, book))
            yield book_data

        next_page = response.css("li.next > a::attr(href)").get()
        if next_page:
            next_url = response.urljoin(next_page)
            yield scrapy.Request(next_url, callback=self.parse)

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

    def __init__(self):
        super().__init__()
        self._driver = self.__set_chrome_driver()
        self._rating_table = {
            "Zero": 0,
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }

    def __set_chrome_driver(self):
        options = Options()
        options.add_argument("--headless=new")
        return webdriver.Chrome(options=options)

    def close(self, reason: str):
        self._driver.quit()

    def parse(self, response: Response, **kwargs):
        for product in response.css(".product_pod"):
            yield self._parse_book_page(response, product)

        next_page = response.css(".pager > .next").css("a::attr(href)").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def _parse_book_page(
            self,
            response: Response,
            product: Selector
    ) -> dict:

        detail_url = response.urljoin(product.css("a::attr(href)").get())
        self._driver.get(detail_url)
        return self._get_book_data()

    def _get_book_data(self):
        article_page = self._driver.find_element(By.ID, "content_inner")
        product_main = article_page.find_element(By.CLASS_NAME, "product_main")
        return {
            "title": product_main.find_element(
                By.TAG_NAME, "h1"
            ).text,
            "price": float(product_main.find_element(
                By.CLASS_NAME, "price_color"
            ).text.replace("£", "")),
            "amount_in_stock": self._get_instock_number(article_page.find_element(
                By.CLASS_NAME, "instock"
            ).text),
            "rating": self._get_rating(article_page.find_element(
                By.CLASS_NAME, "star-rating"
            ).get_attribute("class")),
            "category": self._driver.find_elements(
                By.CSS_SELECTOR, ".breadcrumb > li"
            )[-2].text,
            "description": article_page.find_element(
                By.CSS_SELECTOR, "article > p")
            .text,
            "upc": article_page.find_element(
                By.CSS_SELECTOR, ".table-striped > tbody > tr > td"
            ).text
        }

    def _get_rating(self, classes: str) -> int:
        rating = classes.split()[-1]
        return self._rating_table[rating]

    def _get_instock_number(self, string: str) -> int:
        values = string.split()
        return int(values[-2].replace("(", ""))

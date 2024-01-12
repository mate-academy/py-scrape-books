import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str):
        self.driver.close()

    def parse(self, response: Response, **kwargs):
        for product in response.css(".col-lg-3"):
            detailed_page_info = self._get_info_from_detail_page(response, product)
            yield detailed_page_info

        next_page = response.css(".next > a::attr(href)").get()

        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def _get_info_from_detail_page(self, response: Response, product: Selector):
        detailed_url = response.urljoin(product.css("a::attr(href)").get())
        self.driver.get(detailed_url)

        rating = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        detailed_page_info = {
            "title": self.driver.find_element(By.CLASS_NAME, "product_main").find_element(By.TAG_NAME, "h1").text,
            "price": float(self.driver.find_element(By.CLASS_NAME, "price_color").text.replace("£", "")),
            "amount_in_stock": int(self.driver.find_element(
                By.CLASS_NAME, "availability"
            ).text.replace("(", "").split()[2]),
            "rating": rating[self.driver.find_element(By.CLASS_NAME, "star-rating").get_attribute("class").split()[-1]],
            "category": self.driver.find_element(
                By.TAG_NAME, "tbody"
            ).find_elements(By.TAG_NAME, "tr")[1].find_element(By.TAG_NAME, "td").text,
            "description": self.driver.find_elements(By.TAG_NAME, "p")[3].text,
            "upc": self.driver.find_element(
                By.TAG_NAME, "tbody"
            ).find_elements(By.TAG_NAME, "tr")[0].find_element(By.TAG_NAME, "td").text,
        }

        return detailed_page_info

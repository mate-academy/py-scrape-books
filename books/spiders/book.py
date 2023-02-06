import scrapy
from scrapy import Selector
from scrapy.http import Response

from selenium import webdriver
from selenium.webdriver.common.by import By


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason):
        self.driver.close()

    def detail_info(self, response: Response, book: Selector) -> dict:
        detail_url = response.urljoin(book.css("h3::attr(href)").get())
        self.driver.get(detail_url)

        # upc = self.driver.find_elements(By.TAG_NAME, "td")
        # [1].find_element(By.TAG_NAME, "td").text,

        description = self.driver.find_element(By.CSS_SELECTOR, "article[p]")

        return dict(
            available=self.driver.find_element(By.CLASS_NAME, "availability").text,
            category=self.driver.find_elements(By.CLASS_NAME, "breadcrumb")[-1].text,
            description=description,
            # upc=upc,
        )

    def parse(self, response: Response, **kwargs):
        for book in response.css(".product_pod"):
            book_ = dict(
                title=book.css("h3 > a::attr(title)").get(),
                price=book.css(".price_color::text").get(),
                rating=book.css(".star-rating::attr(class)").get().split()[-1],
            )
            book_.update(self.detail_info(response, book))
            yield book_

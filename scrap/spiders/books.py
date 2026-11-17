import scrapy
from scrapy import Selector, Spider
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from twisted.internet.defer import Deferred


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()

    def close(self, spider: Spider, reason: str,) -> Deferred[None] | None:
        self.driver.close()
        return super().close(spider, reason)

    def parse(self, response):
        dict_rating = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        for product in response.css(".product_pod"):
            result = self.parse_info_in_detail_book(product, response)
            yield {
                "title": product.css("a::attr(title)").get(),
                "price": float(product.css(".price_color::text").get().replace("£", "")),
                "amount_in_stock": result[0],
                "rating": dict_rating[product.css("p::attr(class)").get().split(" ")[1]],
                "category": result[1],
                "description": result[2],
                "upc": result[3],
            }

        next_page = response.css(".pager > li.next")[-1].css("a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_info_in_detail_book(self, product: Selector, response: Response) -> list:
        url = response.urljoin(product.css("a::attr(href)").get())
        self.driver.get(url)
        result = [int(self.driver.find_element(By.CSS_SELECTOR, "p.availability").text.split(" ")[2].replace("(", "")),
                  str(self.driver.find_elements(By.CSS_SELECTOR, "ul.breadcrumb li")[2].find_element(By.TAG_NAME, "a").text),
                  self.driver.find_element(By.CSS_SELECTOR, "#product_description + p").text]
        upcs = self.driver.find_elements(By.TAG_NAME, "tr")[0]
        result.append(upcs.find_element(By.TAG_NAME, "td").text)

        return result

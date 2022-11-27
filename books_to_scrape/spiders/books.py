import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By


class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason):
        self.driver.close()

    def parse(self, response: Response, **kwargs):
        rating = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}

        for book in response.css(".product_pod"):
            yield {
                "title": book.css("h3 > a::attr(title)").get(),
                "price": float(book.css(".price_color::text").get().replace("£", "")),
                "rating": rating[book.css(".star-rating::attr(class)").get().split()[-1].lower()],
                **self.parse_one_book(response, book)
            }

        next_page = response.css(".next > a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_one_book(self, response: Response, book: Selector):
        detail_url = response.urljoin(book.css("h3 > a::attr(href)").get())
        self.driver.get(detail_url)

        return {
            "amount_in_stock": int(self.driver.find_element(By.CLASS_NAME, "instock").text.split()[-2][1:]),
            "category": self.driver.find_elements(By.CSS_SELECTOR, ".breadcrumb > li")[-2].text.lower(),
            "description": self.driver.find_element(By.CSS_SELECTOR, "article > p").text,
            "upc": self.driver.find_element(By.CSS_SELECTOR, "tbody td").text,
        }

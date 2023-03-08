import scrapy
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By

from helpers import parse_page


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self):
        super(BookSpider, self).__init__()
        self.driver = webdriver.Chrome()

    def close(self, reason):
        self.driver.close()

    def parse(self, response: Response, **kwargs):
        self.driver.get(response.url)
        links_detail = self.driver.find_elements(By.CSS_SELECTOR, "h3 > a")
        for link in links_detail:
            link.click()

            yield parse_page(self.driver)

            self.driver.back()

        next_button = response.css("li.next > a").css("a::attr(href)").get()

        if next_button is not None:
            next_page_url = response.urljoin(next_button)
            yield scrapy.Request(next_page_url, callback=self.parse)

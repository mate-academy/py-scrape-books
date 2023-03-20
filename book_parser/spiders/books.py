from selenium import webdriver
from scrapy import Spider
from scrapy.http import HtmlResponse

from book_parser.help_functions import parse_book_details


class BooksSpider(Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["http://books.toscrape.com/"]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def parse(self, response: HtmlResponse) -> None:
        book_links = response.css(".product_pod a::attr(href)").getall()
        yield from response.follow_all(book_links, self.parse_book)

        next_page_link = response.css(".next a::attr(href)").get()
        if next_page_link:
            yield response.follow(next_page_link, self.parse)

    def parse_book(self, response: HtmlResponse) -> None:
        self.driver.get(response.url)
        yield from parse_book_details(response)

    def closed(self) -> None:
        self.driver.quit()

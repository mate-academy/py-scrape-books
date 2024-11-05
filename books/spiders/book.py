import scrapy
from scrapy import Selector
from scrapy.http import Response
from selenium import webdriver


class BookSpider(scrapy.Spider):
    name = "book"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str) -> None:
        self.driver.close()

    def parse(self, response: Response, **kwargs) -> dict:
        for book in response.css(".product_pod"):
            info = self._parse_additional_info(response, book)
            yield {
                "title": book.css("a::attr(title)").get(),
                "price": book.css(".price_color::text").get(),
                "amount_in_stock": info["amount_in_stock"],
                "rating": info["rating"],
                "category": info["category"],
                "description": info["description"],
                "upc": info["upc"],
            }

    def _parse_additional_info(
            self,
            response: Response,
            book: Selector
    ) -> dict:
        detail_url = response.urljoin(book.css("a::attr(href)").get())
        self.driver.get(detail_url)

        detail_page = self.driver.page_source
        detail_response = Selector(text=detail_page)
        rating = detail_response.css(
            ".star-rating::attr(class)"
        ).get().split()[-1]
        if rating == "One":
            rating = 1
        elif rating == "Two":
            rating = 2
        elif rating == "Three":
            rating = 3
        elif rating == "Four":
            rating = 4
        elif rating == "Five":
            rating = 5
        info = {
            "amount_in_stock": detail_response.css(
                ".table-striped tr:nth-of-type(6) td::text"
            ).get().split("(")[-1].split()[0],
            "rating": rating,
            "category": detail_response.css(
                "ul.breadcrumb li:nth-last-child(2) a::text"
            ).get(),
            "description": detail_response.css(
                "#product_description + p::text"
            ).get(),
            "upc": detail_response.css(
                ".table-striped tr:nth-of-type(1) td::text"
            ).get(),
        }

        return info

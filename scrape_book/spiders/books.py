import scrapy
from scrapy.http import Response

from selenium import webdriver


WORD_TO_DIGIT_MAP = {
        "Zero": 0,
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }


class BooksSpider(scrapy.Spider):
    """
    This spider scrapes book details from books.toscrape.com.
    """
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, **kwargs) -> None:
        """
        Initialize webdriver.
        """
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    @staticmethod
    def _get_numeric_price(price: str) -> float:
        return float(price.replace("£", ""))

    @staticmethod
    def _get_numeric_amount_in_stock(amount_in_stock: str) -> int:
        return int(amount_in_stock.re(r"In stock \((\d+) available\)")[0])

    def parse(self, response: Response, **kwargs) -> None:
        """
        Parse the response.
        """
        for book in response.css(".product_pod > h3 > a"):
            yield response.follow(book, callback=self.parse_detail_book_info)

        next_button = response.css(".pager > li")[-1].css("a::attr(href)").get()

        if next_button is not None:
            next_page_url = response.urljoin(next_button)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_detail_book_info(self, response: Response):
        """
        Parse book details.
        """
        yield {
            "title": response.css(".product_main > h1::text").get(),
            "price": self._get_numeric_price(response.css(".price_color::text").get()),
            "amount_in_stock": self._get_numeric_amount_in_stock(response.css(".instock.availability::text")),
            "rating": WORD_TO_DIGIT_MAP[response.css("p.star-rating::attr(class)").get().split(" ")[1]],
            "category": response.css("ul.breadcrumb > li:nth-last-child(2) > a::text").get(),
            "description": response.css(".product_page > p::text").get(),
            "upc": response.css(".table td::text").getall()[0],
        }

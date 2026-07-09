import scrapy
from scrapy.http import Response

from book_scraper.items import BookItem

RATING_TO_INT = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> None:
        for book in response.css(".product_pod h3 a::attr(href)").getall():
            yield response.follow(book, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> None:
        yield BookItem(
            title=self._parse_title(response),
            price=self._parse_price(response),
            amount_in_stock=self._parse_amount_in_stock(response),
            rating=self._parse_rating(response),
            category=self._parse_category(response),
            description=self._parse_description(response),
            upc=self._parse_upc(response),
        )

    @staticmethod
    def _parse_title(response: Response) -> str:
        return response.css("h1::text").get()

    @staticmethod
    def _parse_price(response: Response) -> float:
        price = response.css(".price_color::text").get()
        return float(price.replace("£", ""))

    @staticmethod
    def _parse_amount_in_stock(response: Response) -> int:
        text = " ".join(
            response.css(".product_main .availability::text").getall()
        )
        digits = "".join(char for char in text if char.isdigit())
        return int(digits) if digits else 0

    @staticmethod
    def _parse_rating(response: Response) -> int:
        rating = response.css("p.star-rating::attr(class)").get()
        word = rating.replace("star-rating", "").strip()
        return RATING_TO_INT.get(word, 0)

    @staticmethod
    def _parse_category(response: Response) -> str:
        return response.css(".breadcrumb li a::text").getall()[-1]

    @staticmethod
    def _parse_description(response: Response) -> str:
        return response.css("#product_description ~ p::text").get(default="")

    @staticmethod
    def _parse_upc(response: Response) -> str:
        return response.css("table tr td::text").get()

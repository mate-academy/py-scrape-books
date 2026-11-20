from collections.abc import Iterator

import scrapy
from scrapy.http import Response

from books.dto import BookItem


RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    def parse(self, response: Response, **kwargs) -> Iterator[scrapy.Request]:
        """Follow every book on the catalogue page, then the next page."""
        yield from response.follow_all(
            css="article.product_pod h3 a", callback=self.parse_book
        )
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
    def parse_book(self, response: Response) -> Iterator[BookItem]:
        yield BookItem(
            title=response.css(".product_main h1::text").get(),
            price=self.parse_price(response),
            amount_in_stock=self.parse_amount_in_stock(response),
            rating=self.parse_rating(response),
            category=response.css(
                ".breadcrumb li:nth-child(3) a::text"
            ).get(),
            description=response.css(
                "#product_description + p::text"
            ).get(default=""),
            upc=response.xpath(
                "//th[text()='UPC']/following-sibling::td/text()"
            ).get(),
        )
    @staticmethod
    def parse_price(response: Response) -> float:
        price = response.css(".product_main .price_color::text").re_first(
            r"[\d.]+", default="0"
        )
        return float(price)
    @staticmethod
    def parse_amount_in_stock(response: Response) -> int:
        amount = response.css(".product_main .availability::text").re_first(
            r"\d+", default="0"
        )
        return int(amount)
    @staticmethod
    def parse_rating(response: Response) -> int:
        rating_word = response.css(
            ".product_main .star-rating::attr(class)"
        ).re_first(r"star-rating (\w+)", default="")
        return RATINGS.get(rating_word, 0)

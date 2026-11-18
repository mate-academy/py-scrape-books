from typing import Iterator, Optional

import scrapy
from scrapy.http import Response

from books_scraper.items import BooksScraperItem

RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response) -> Iterator[scrapy.Request]:
        yield from response.follow_all(
            css="article.product_pod h3 a",
            callback=self.parse_book,
        )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response) -> Iterator[BooksScraperItem]:
        yield BooksScraperItem(
            title=response.css("div.product_main h1::text").get(),
            price=self.parse_price(response),
            amount_in_stock=self.parse_amount_in_stock(response),
            rating=self.parse_rating(response),
            category=response.css(
                "ul.breadcrumb li:nth-child(3) a::text"
            ).get(),
            description=response.css("#product_description + p::text").get(),
            upc=response.xpath(
                "//th[text()='UPC']/following-sibling::td/text()"
            ).get(),
        )

    @staticmethod
    def parse_price(response: Response) -> float:
        return float(response.css("p.price_color::text").re_first(r"[\d.]+"))

    @staticmethod
    def parse_amount_in_stock(response: Response) -> int:
        return int(response.css("p.availability::text").re_first(r"\d+"))

    @staticmethod
    def parse_rating(response: Response) -> Optional[int]:

        rating_class = response.css("p.star-rating::attr(class)").get()
        return RATINGS.get(rating_class.split()[-1])

import re
from typing import Generator

import scrapy
from scrapy.http import Response

from book_scraper.items import BookScraperItem


class BookSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        "https://books.toscrape.com/catalogue/category/books_1/index.html"
    ]

    def parse(self, response: Response, **kwargs) -> Generator:
        for product in response.css(".product_pod"):
            book_href = product.css("a::attr(href)").get()
            book_detail_url = response.urljoin(book_href)
            yield response.follow(book_detail_url, callback=self.parse_book)

        next_page = response.css(".pager .next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def get_available_in_stock(response: Response) -> int:
        amount_text = (
            response.css(".product_main p.instock.availability::text")
            .getall()[-1].strip()
        )
        match = re.search(r"((\d+))", amount_text)
        return int(match.group(1)) if match else 0

    @staticmethod
    def get_rating(response: Response) -> int:
        ratings = {"One": 1,
                   "Two": 2,
                   "Three": 3,
                   "Four": 4,
                   "Five": 5}
        book_rating = (
            response.css(".star-rating::attr(class)").get().split()[-1]
        )
        return ratings.get(book_rating, 0)

    def parse_book(self, response: Response) -> Generator:
        title = response.css("h1::text").get()
        price = float(response.css(".price_color::text").get().lstrip("£"))
        category = response.css(".breadcrumb a::text").getall()[-1].strip()
        description = response.xpath(
            '//div[@id="product_description"]/following-sibling::p[1]/text()'
        ).get(default="")
        upc = response.css(".table td::text").getall()[0]

        book = BookScraperItem(
            title=title,
            price=price,
            amount_in_stock=self.get_avaliable_in_stock(response),
            category=category,
            description=description,
            upc=upc
        )

        yield book

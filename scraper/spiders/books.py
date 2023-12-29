from typing import Any, Generator

import scrapy
from scrapy.http import Response

from scraper.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse_book(self, response: Response) -> BookItem:
        book = response.css(".product_main")
        return BookItem(
            title=book.css("h1::text").get(),
            price=float(book.css(".price_color::text").get()[1:]),
            amount_in_stock=int(book.css(".instock::text")[1].re(r"(\d+)")[0]),
            rating=book.css(".star-rating::attr(class)").get().split()[1],
            category=response.css(".breadcrumb li a::text").getall()[2],
            description=response.css("#product_description + p::text").get(),
            upc=response.css("table td::text").get(),
        )

    def parse(self, response: Response) -> Generator[BookItem, Any, None]:
        for book_link in response.css(".col-xs-6 h3 a"):
            yield response.follow(book_link, callback=self.parse_book)
        if next_page := response.css(".pager .next a"):
            yield response.follow(next_page[0], callback=self.parse)

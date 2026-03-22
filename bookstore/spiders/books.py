from typing import Any, Generator

import scrapy
from scrapy import Request
from scrapy.http import HtmlResponse, Response

from bookstore.items import BookstoreItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(
            self,
            response:
            Response,
            **kwargs
    ) -> Generator[Request, Any, None]:
        books = response.css("article.product_pod")

        for book in books:
            relative_url = book.css("h3 a::attr(href)").get()
            book_url = response.urljoin(relative_url)

            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(
            self,
            response: HtmlResponse,
            **kwargs
    ) -> Generator[BookstoreItem, Any, None]:
        mapping = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        item = BookstoreItem()

        rating_class = response.css("p.star-rating::attr(class)").get()
        price = response.css("p.price_color::text").get()

        rating = None
        if rating_class:
            rating_name = rating_class.split()[-1]
            rating = mapping.get(rating_name)

        item["title"] = response.css("h1::text").get()
        item["price"] = price.replace("£", "") if price else None
        item["amount_in_stock"] = response.css(
            "table tr:contains('Availability') td::text"
        ).re_first(r"\d+")
        item["rating"] = rating
        item["category"] = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get()
        item["description"] = response.css(
            "#product_description ~ p::text"
        ).get()
        item["upc"] = response.css("table tr:contains('UPC') td::text").get()

        yield item

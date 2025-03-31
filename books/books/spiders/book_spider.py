from typing import Generator, Any

import scrapy
from scrapy.http import Response

from books.items import BooksItem


class BookSpider(scrapy.Spider):
    name = "book_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    @staticmethod
    def parse_book_detail(
        response: Response
    ) -> Generator[BooksItem, Any, None]:
        book = response.css(".page_inner")
        book_content = book.css(".content")

        book_item = BooksItem()

        book_item["title"] = (
            book_content.css(".product_main h1::text").get()
            or "No title"
        )
        price = book_content.css("p.price_color::text").get()
        book_item["price"] = price.replace("£", "") if price else "0.00"
        book_item["amount_in_stock"] = (
            book_content.css(
                "p.instock.availability::text"
            ).re_first(r"\((\d+) available\)") or "0"
        )
        book_item["rating"] = (
            book_content.css(
                "p.star-rating::attr(class)"
            ).re_first(r"star-rating (\w+)") or "No rating"
        )
        book_item["category"] = (
            book.css("ul.breadcrumb li:nth-child(3) a::text").get()
            or "No category"
        )
        description = (
            book_content.css("div#product_description ~ p::text").get()
            or "No description"
        )
        if description.endswith(" ...more"):
            description = description[:-7]
        book_item["description"] = description
        book_item["upc"] = (
            book_content.css(
                "table.table-striped tr:nth-child(1) td::text"
            ).get() or "No UPC"
        )

        yield book_item

    def parse(
        self,
        response: Response,
        **kwargs
    ) -> Generator[scrapy.Request, Any, None]:
        for book in response.css(".product_pod"):
            book_detail_url = response.urljoin(
                book.css("h3 a::attr(href)").get()
            )
            yield scrapy.Request(
                url=book_detail_url, callback=self.parse_book_detail
            )

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
